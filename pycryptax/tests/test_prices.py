import unittest
import os
from datetime import datetime
from decimal import Decimal

from pycryptax.prices import Prices

class TestPrices(unittest.TestCase):

    def test_midprice(self):
        priceData = Prices('usd', os.path.dirname(__file__) + '/../../examples/prices')
        mid = priceData.get('gbp', datetime(2019, 4, 15))
        self.assertAlmostEqual(mid, Decimal(1.3188))

        self.assertAlmostEqual(priceData.get('gbp', datetime(2019, 5, 15)), Decimal(1.3049))