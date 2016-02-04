import unittest
from stockfish import Stockfish


class TestStockfish(unittest.TestCase):

    def setUp(self):
        self.stockfish = Stockfish()

    def testRun(self):
        best_move = self.stockfish.get_best_move()
        self.assertIn(best_move, ('e2e4', 'g1f3',))

        self.stockfish.set_position(['e2e4', 'e7e6'])
        best_move = self.stockfish.get_best_move()
        self.assertIn(best_move, ('d2d4', 'g1f3',))


if __name__ == '__main__':
    unittest.main()
