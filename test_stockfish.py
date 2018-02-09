"""Tests for Stockfish."""


import unittest
from stockfish import Stockfish


class TestStockfish(unittest.TestCase):

    def setUp(self):
        self.stockfish = Stockfish()

    def test_get_best_move(self):
        best_move = self.stockfish.get_best_move()
        self.assertIn(best_move, ('e2e4', 'g1f3',))

        self.stockfish.set_position(['e2e4', 'e7e6'])
        best_move = self.stockfish.get_best_move()
        self.assertIn(best_move, ('d2d4', 'g1f3',))

        # mate
        self.stockfish.set_position(['f2f3', 'e7e5', 'g2g4', 'd8h4'])
        self.assertFalse(self.stockfish.get_best_move())

    def test_set_fen_position(self):
        self.stockfish.set_fen_position("7r/1pr1kppb/2n1p2p/2NpP2P/5PP1/1P6/P6K/R1R2B2 w - - 1 27")
        self.assertTrue(self.stockfish.is_move_correct('f4f5'))
        self.assertFalse(self.stockfish.is_move_correct('a1c1'))

    def test_is_move_correct(self):
        self.assertFalse(self.stockfish.is_move_correct('e2e1'))
        self.assertTrue(self.stockfish.is_move_correct('a2a3'))
        self.stockfish.set_position(['e2e4', 'e7e6'])
        self.assertFalse(self.stockfish.is_move_correct('e2e1'))
        self.assertTrue(self.stockfish.is_move_correct('a2a3'))


if __name__ == '__main__':
    unittest.main()
