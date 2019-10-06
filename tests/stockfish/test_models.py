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
        assert stockfish.get_best_move() is None

    def test_set_fen_position(self, stockfish):
        stockfish.set_fen_position(
            "7r/1pr1kppb/2n1p2p/2NpP2P/5PP1/1P6/P6K/R1R2B2 w - - 1 27"
        )
        assert stockfish.is_move_correct("f4f5") is True
        assert stockfish.is_move_correct("a1c1") is False

    def test_set_fen_position_reset(self, stockfish):
        stockfish.set_fen_position(
            "7r/1pr1kppb/2n1p2p/2NpP2P/5PP1/1P6/P6K/R1R2B2 w - - 1 27"
        )
        stockfish.set_fen_position("3kn3/p5rp/1p3p2/3B4/3P1P2/2P5/1P3K2/8 w - - 0 53")
        assert stockfish.is_move_correct("d5a8") is True
        assert stockfish.is_move_correct("f2a2") is False

    def test_is_move_correct_first_move(self, stockfish):
        assert stockfish.is_move_correct("e2e1") is False
        assert stockfish.is_move_correct("a2a3") is True

    def test_is_move_correct_not_first_move(self, stockfish):
        stockfish.set_position(["e2e4", "e7e6"])
        assert stockfish.is_move_correct("e2e1") is False
        assert stockfish.is_move_correct("a2a3") is True

    @pytest.mark.parametrize(
        "value",
        [
            "info",
            "depth",
            "seldepth",
            "multipv",
            "score",
            "mate",
            "-1",
            "nodes",
            "nps",
            "tbhits",
            "time",
            "pv",
            "h2g1",
            "h4g3",
        ],
    )
    def test_last_info(self, stockfish, value):
        stockfish.set_fen_position("r6k/6b1/2b1Q3/p6p/1p5q/3P2PP/5r1K/8 w - - 1 31")
        stockfish.get_best_move()
        assert value in stockfish.info
