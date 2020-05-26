import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from pycryptax.csvdata import CSVTransactionGains, TransactionGainTx
from pycryptax.gains import CapitalGainCalculator

class TestGains(unittest.TestCase):

    @patch('pycryptax.csvdata.CSVDateMap._processFile')
    @patch('os.path.isdir')
    def test_simple(self, MockClass, mmm):
        config = {'isdir.return_value': False}
        patcher = patch('os.path', **config)
        mock_thing = patcher.start()

        config2 = {'_processFile.return_value': None}
        patcher2 = patch('pycryptax.csvdata.CSVDateMap', **config2)
        mock_thing2 = patcher2.start()

        gainData = CSVTransactionGains("", requireDir=False)
        gainData.insert(
            datetime(2020, 1, 1),
            TransactionGainTx(
                'MSFT', 50, Decimal(1.0), Decimal(0.5)
            )
        )
        gainData.insert(
            datetime(2020, 1, 2),
            TransactionGainTx(
                'MSFT', -20, Decimal(2.0), Decimal(0.6)
            )
        )
        gainData.insert(
            datetime(2020, 1, 3),
            TransactionGainTx(
                'MSFT', 10, Decimal(3.0), Decimal(0.7)
            )
        )

        c = CapitalGainCalculator(gainData, None, datetime(2019, 4, 6), datetime(2020, 4, 5))
        c.printSummary()

