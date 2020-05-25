import copy, datetime
from decimal import Decimal
from enum import Enum

from pycryptax import util, output, datemap
from pycryptax.csvdata import CSVTransactionGains


class AssetPool():

    def __init__(self):
        self.totalQuantity = 0
        self.totalCost = 0

    def add(self, quantity, cost):
        self.totalQuantity += quantity
        self.totalCost += cost

    def dispose(self, quantity):

        if quantity > self.totalQuantity:
            raise ValueError(
                "Quantity of asset being disposed, is more than existing. {} > {}"
                .format(quantity, self.totalQuantity)
            )

        cost = self.totalCost * quantity / self.totalQuantity
        self.totalQuantity -= quantity
        self.totalCost -= cost

        return cost

    def __repr__(self):
        return "AssetPool({}, {})".format(self.totalQuantity, self.totalCost)

class AggregateDayTxs():

    def __init__(self):

        self.acquireAmt = 0
        self.acquireVal = 0

        self.disposeAmt = 0
        self.disposeVal = 0

    def acquire(self, amt, val):
        self.acquireAmt += amt
        self.acquireVal += val

    def dispose(self, amt, val):
        self.disposeAmt += amt
        self.disposeVal += val

class Gain():

    def __init__(self, cost=0, value=0):
        self._value = value
        self._cost = cost

    def __iadd__(self, b):
        self._value += b._value
        self._cost += b._cost
        return self

    def cost(self):
        return self._cost

    def value(self):
        return self._value

    def gain(self):
        return self._value - self._cost

class Rule(Enum):
    SAME_DAY = "SAME DAY"
    BED_AND_BREAKFASTING = "BED AND BREAKFASTING"

class CapitalGainCalculator():

    def __init__(
        self, gainData: CSVTransactionGains, priceData, start, end, summary=True, disposals=True
    ):

        self._start = start
        self._end = end
        self._includeSummary = summary
        self._includeDisposals = disposals

        if summary:
            self._assetGain = {}
            self._totalGain = Gain()

        if disposals:
            self._disposals = datemap.DateMap()

        self._assetPoolsAtEnd = {}
        self._assetPools = {}

        # self._priceData = priceData

        # Obtain total acquisition and disposal values for each day for every
        # asset

        assetTxs = {}

        def getDayTxForAsset(asset, date):

            if asset not in assetTxs:
                assetTxs[asset] = datemap.DateMap()

            dayTxs = assetTxs[asset]

            if date not in dayTxs:
                return dayTxs.insert(date, AggregateDayTxs())

            return dayTxs[date]

        for date, tx in gainData:
            print(tx)
            if tx.amount > 0:
                # Acquisition

                getDayTxForAsset(tx.asset, date).acquire(
                    tx.amount,
                    tx.amount * tx.price
                )

            if tx.amount < 0:
                # Disposal

                getDayTxForAsset(tx.asset, date).dispose(
                    -tx.amount,
                    -tx.amount * tx.price
                )

        def applyGain(asset, gain, date):

            if date < start or date > end:
                return

            if self._includeSummary:
                self._totalGain += gain
                util.addToDictKey(self._assetGain, asset, gain)

            if self._includeDisposals:
                self._disposals.insert(date, (asset, gain))

        def match(asset, date, matchDate, disposeTx, acquireTx, rule):

            # Get amount that can be matched
            amount = min(disposeTx.disposeAmt, acquireTx.acquireAmt)

            if amount == 0:
                # Cannot match nothing
                return

            # Get proportion of cost
            cost = acquireTx.acquireVal * amount / acquireTx.acquireAmt

            # Get proportion of disposal value
            value = disposeTx.disposeVal * amount / disposeTx.disposeAmt

            # Apply gain/loss
            applyGain(asset, Gain(cost, value), date)

            # Adjust data to remove amounts and report asset values that have
            # been accounted for

            disposeTx.disposeAmt -= amount
            acquireTx.acquireAmt -= amount

            disposeTx.disposeVal -= value
            acquireTx.acquireVal -= cost

            profit = value - cost
            print("SELL: {amount} {asset} on {dt} at £{price:.02f} gives {gain_or_loss} of {profit:.02f}".format(
                amount=amount,
                asset=asset,
                dt=date,
                gain_or_loss='GAIN' if profit >= 0 else 'LOSS',
                price=cost / amount,
                profit=profit,
            ))
            print("Matches with:\n"
                  "BUY: {amount} {asset} shares bought on {dt} at £{price:0.2f} according to {rule} rule\n\n".format(
                asset=asset,
                amount=amount,
                dt=matchDate,
                price=cost / amount,
                rule=rule.value,
            ))

        for asset, dayTxs in assetTxs.items():

            # Same-day rule: Match disposals to acquisitions that happen on the same day

            for date, tx in dayTxs:
                match(asset, date, date, tx, tx, Rule.SAME_DAY)

            # Bed and breakfasting rule
            # Match disposals to nearest acquisitions from 1->30 days afterwards

            for date, tx in dayTxs:

                # Only process disposals
                if tx.disposeAmt == 0:
                    continue

                # Loop though transactions in range to match against
                for matchDate, matchTx in dayTxs.range(
                    date + datetime.timedelta(days=1),
                    date + datetime.timedelta(days=30)
                ):
                    match(asset, date, matchDate, tx, matchTx, Rule.BED_AND_BREAKFASTING)

            # Process section 104 holdings from very beginning but only count gains
            # realised between start and end.

            for date, tx in dayTxs:

                # Only an acquisition or disposal, not both allowed.
                # Should have been previously matched
                assert(not (tx.acquireAmt != 0 and tx.disposeAmt != 0))

                if tx.acquireAmt != 0:

                    # Adjust section 104 holding

                    if asset not in self._assetPools:
                        self._assetPools[asset] = AssetPool()

                    self._assetPools[asset].add(tx.acquireAmt, tx.acquireVal)

                if tx.disposeAmt != 0:

                    if asset not in self._assetPools:
                        raise ValueError("Disposing of an asset not acquired")

                    average_price = 0

                    # Adjust section 104 holding and get cost
                    try:
                        total_cost = self._assetPools[asset].totalCost
                        total_amount = self._assetPools[asset].totalQuantity
                        average_price = total_cost / total_amount
                        cost = self._assetPools[asset].dispose(tx.disposeAmt)
                    except ValueError as e:
                        print(util.getPrettyDate(date) + " (" + asset + "): " + str(e))
                        raise e

                    # Apply gain/loss
                    applyGain(asset, Gain(cost, tx.disposeVal), date)
                    profit = tx.disposeVal - cost
                    print("SELL: {amount} {asset} on {dt} at £{price:.02f} gives {gain_or_loss} of £{profit:.02f}".format(
                        amount=tx.disposeAmt,
                        asset=asset,
                        dt=date,
                        gain_or_loss='GAIN' if profit >= 0 else 'LOSS',
                        price=tx.disposeVal / tx.disposeAmt,
                        profit=profit,
                    ))
                    print("Matches with:\nBUY: SECTION 104 HOLDING. {amount} {asset} shares of £{total_amount} "
                          "bought at average price of £{average_price}\n\n".format(
                        asset=asset,
                        amount=tx.disposeAmt,
                        total_amount=total_amount,
                        average_price=average_price,
                    ))

                if date <= end:
                    # Update asset pools up until the end of the range to get the
                    # section 104 holdings at the point of the end of the range
                    self._assetPoolsAtEnd[asset] = copy.deepcopy(self._assetPools[asset])

    def printSummary(self):

        output.printCalculationTitle("CAPITAL GAIN", self._start, self._end)

        table = output.OutputTable(4)
        table.appendRow("ASSET", "ACQUISITION COST", "DISPOSAL VALUE", "GAIN / LOSS")
        table.appendGap()

        for k, v in self._assetGain.items():
            table.appendRow(k, v.cost(), v.value(), v.gain())

        table.appendGap()
        table.appendRow(
            "TOTAL", self._totalGain.cost(), self._totalGain.value(),
            self._totalGain.gain()
        )

        table.print()

        # print("SECTION 104 HOLDINGS AS OF {}:\n".format(util.getPrettyDate(self._end)))
        #
        # table = output.OutputTable(5)
        # table.appendRow("ASSET", "AMOUNT", "COST", "VALUE", "UNREALISED GAIN")
        # table.appendGap()
        #
        # totalCost = Decimal(0)
        # totalValue = Decimal(0)

        # for asset, pool in self._assetPoolsAtEnd.items():
        #
        #     value = pool.totalQuantity * 1   # TODO: fix: self._priceData.get(asset, self._end)
        #
        #     totalCost += pool.totalCost
        #     totalValue += value
        #
        #     table.appendRow(
        #         asset, pool.totalQuantity, pool.totalCost, value, value - pool.totalCost
        #     )
        #
        # table.appendGap()
        # table.appendRow("", "TOTAL", totalCost, totalValue, totalValue - totalCost)
        #
        # table.print()


