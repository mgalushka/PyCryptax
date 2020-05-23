import unittest
from datetime import datetime

from pycryptax.datemap import DateMap

class TestDateMap(unittest.TestCase):

    def test_empty(self):
        dm = DateMap()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 3)

        counter = 0
        for _ in dm.range(start, end):
            counter += 1
        self.assertEqual(counter, 0)

    def test_new(self):
        dm = DateMap()
        start = datetime(2020, 1, 1)
        end = datetime(2020, 1, 3)

        dm.insert(datetime(2020, 1, 1), {'lol': 17})
        dm.insert(datetime(2020, 1, 2), {'lol': 18})
        dm.insert(datetime(2020, 1, 4), {'lol': 19})
        counter = 0
        for _ in dm.range(start, end):
            counter += 1
        self.assertEqual(counter, 2)

    def test_index(self):
        dm = DateMap()

        dm.insert(datetime(2020, 1, 2), {'lol': 17})
        dm.insert(datetime(2020, 1, 1), {'lol': 18})
        dm.insert(datetime(2020, 1, 4), {'lol': 19})

        # check sorted order
        self.assertEqual(dm[0][1]['lol'], 18)
        self.assertEqual(dm[1][1]['lol'], 17)
        self.assertEqual(dm[2][1]['lol'], 19)

