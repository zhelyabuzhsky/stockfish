import unittest
from pystockfish import *


class TestStockfish(unittest.TestCase):
    def setUp(self):
        self.stockfish = Stockfish()

    def testRun(self):
        best_move = self.stockfish.get_best_move()
        self.assertEqual(best_move, 'e2e4')

        self.stockfish.set_position(['e2e4', 'e7e6'])
        best_move = self.stockfish.get_best_move()
        self.assertEqual(best_move, 'd2d4')


if __name__ == '__main__':
    unittest.main()
