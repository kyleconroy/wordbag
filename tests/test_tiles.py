import unittest
from wordbag import main

class TileTest(unittest.TestCase):

    def test_correct_count(self):
        self.assertEquals(len(main.TILES), 27)

    def test_total_count(self):
        self.assertEquals(sum([t[2] for t in main.TILES]), 100)

