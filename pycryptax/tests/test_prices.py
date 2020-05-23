import unittest
import os
from datetime import datetime

from pycryptax.prices import Prices

class TestPrices(unittest.TestCase):

    def test_midprice(self):
        priceData = Prices('usd', os.path.dirname(__file__) + '/../../examples/prices')
        mid = priceData.get('gbp', datetime(2019, 4, 15))
        self.assertEqual(mid, 12)

        self.assertEqual(priceData.get('gbp', datetime(2019, 5, 15)), 13)