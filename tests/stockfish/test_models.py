"""Tests for Stockfish."""

import pytest
from stockfish import Stockfish


class TestStockfish:
    @pytest.fixture
    def stockfish(self):
        return Stockfish()

    def test_get_best_move_first_move(self, stockfish):
        best_move = stockfish.get_best_move()
        assert best_move in ("e2e4", "g1f3", "b1c3")

    def test_get_best_move_not_first_move(self, stockfish):
        stockfish.set_position(["e2e4", "e7e6"])
        best_move = stockfish.get_best_move()
        assert best_move in ("d2d4", "g1f3")

    def test_get_best_move_mate(self, stockfish):
        stockfish.set_position(["f2f3", "e7e5", "g2g4", "d8h4"])
        assert stockfish.get_best_move() is False

    def test_set_fen_position(self, stockfish):
        stockfish.set_fen_position(
            "7r/1pr1kppb/2n1p2p/2NpP2P/5PP1/1P6/P6K/R1R2B2 w - - 1 27"
        )
        assert stockfish.is_move_correct("f4f5") is True
        assert stockfish.is_move_correct("a1c1") is False

    def test_is_move_correct_first_move(self, stockfish):
        assert stockfish.is_move_correct("e2e1") is False
        assert stockfish.is_move_correct("a2a3") is True

    def test_is_move_correct_not_first_move(self, stockfish):
        stockfish.set_position(["e2e4", "e7e6"])
        assert stockfish.is_move_correct("e2e1") is False
        assert stockfish.is_move_correct("a2a3") is True
    
    def test_last_info(self, stockfish):
        stockfish.set_fen_position(
            "r6k/6b1/2b1Q3/p6p/1p5q/3P2PP/5r1K/8 w - - 1 31"
        )
        best_move = stockfish.get_best_move()
        assert self.info == 'info depth 2 seldepth 3 multipv 1 score mate -1 nodes 11 nps 5500 tbhits 0 time 2 pv h2g1 h4g3'
