import pytest

from stockfish import Stockfish


class TestStockfish:
    @pytest.fixture
    def stockfish(self):
        return Stockfish()

    def test_get_best_move_first_move(self, stockfish):
        best_move = stockfish.get_best_move()
        assert best_move in (
            "e2e3",
            "e2e4",
            "g1f3",
            "b1c3",
            "d2d4",
        )

    def test_get_best_move_time_first_move(self, stockfish):
        best_move = stockfish.get_best_move_time(1000)
        assert best_move in ("e2e3", "e2e4", "g1f3", "b1c3")

    def test_set_position_resets_info(self, stockfish):
        stockfish.set_position(["e2e4", "e7e6"])
        stockfish.get_best_move()
        assert stockfish.info != ""
        stockfish.set_position(["e2e4", "e7e6"])
        assert stockfish.info == ""

    def test_get_best_move_not_first_move(self, stockfish):
        stockfish.set_position(["e2e4", "e7e6"])
        best_move = stockfish.get_best_move()
        assert best_move in ("d2d4", "g1f3")

    def test_get_best_move_time_not_first_move(self, stockfish):
        stockfish.set_position(["e2e4", "e7e6"])
        best_move = stockfish.get_best_move_time(1000)
        assert best_move in ("d2d4", "g1f3")

    def test_get_best_move_checkmate(self, stockfish):
        stockfish.set_position(["f2f3", "e7e5", "g2g4", "d8h4"])
        assert stockfish.get_best_move() is None

    def test_get_best_move_time_checkmate(self, stockfish):
        stockfish.set_position(["f2f3", "e7e5", "g2g4", "d8h4"])
        assert stockfish.get_best_move_time(1000) is None

    def test_set_fen_position(self, stockfish):
        stockfish.set_fen_position(
            "7r/1pr1kppb/2n1p2p/2NpP2P/5PP1/1P6/P6K/R1R2B2 w - - 1 27"
        )
        assert stockfish.is_move_correct("f4f5") is True
        assert stockfish.is_move_correct("a1c1") is False

    def test_castling(self, stockfish):
        assert stockfish.is_move_correct("e1g1") is False
        stockfish.set_fen_position(
            "rnbqkbnr/ppp3pp/3ppp2/8/4P3/5N2/PPPPBPPP/RNBQK2R w KQkq - 0 4"
        )
        assert stockfish.is_move_correct("e1g1") is True

    def test_set_fen_position_mate(self, stockfish):
        stockfish.set_fen_position("8/8/8/6pp/8/4k1PP/8/r3K3 w - - 12 53")
        assert stockfish.get_best_move() is None
        assert stockfish.info == ""

    def test_clear_info_after_set_new_fen_position(self, stockfish):
        stockfish.set_fen_position("8/8/8/6pp/8/4k1PP/r7/4K3 b - - 11 52")
        stockfish.get_best_move()
        stockfish.set_fen_position("8/8/8/6pp/8/4k1PP/8/r3K3 w - - 12 53")
        assert stockfish.info == ""

    def test_set_fen_position_starts_new_game(self, stockfish):
        stockfish.set_fen_position(
            "7r/1pr1kppb/2n1p2p/2NpP2P/5PP1/1P6/P6K/R1R2B2 w - - 1 27"
        )
        stockfish.get_best_move()
        assert stockfish.info != ""
        stockfish.set_fen_position("3kn3/p5rp/1p3p2/3B4/3P1P2/2P5/1P3K2/8 w - - 0 53")
        assert stockfish.info == ""

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

    def test_set_skill_level(self, stockfish):
        stockfish.set_fen_position(
            "rnbqkbnr/ppp2ppp/3pp3/8/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1"
        )

        assert stockfish.get_parameters()["Skill Level"] == 20

        stockfish.set_skill_level(1)
        assert stockfish.get_best_move() in (
            "b2b3",
            "b2b3",
            "d2d3",
            "d2d4",
            "b1c3",
            "d1e2",
            "g2g3",
        )
        assert stockfish.get_parameters()["Skill Level"] == 1

        stockfish.set_skill_level(20)
        assert stockfish.get_best_move() in ("d2d4",)
        assert stockfish.get_parameters()["Skill Level"] == 20

    def test_set_elo_rating(self, stockfish):
        stockfish.set_fen_position(
            "rnbqkbnr/ppp2ppp/3pp3/8/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1"
        )

        assert stockfish.get_parameters()["UCI_Elo"] == 1350

        stockfish.set_elo_rating(2000)
        assert stockfish.get_best_move() in (
            "b2b3",
            "b2b3",
            "d2d3",
            "d2d4",
            "b1c3",
            "d1e2",
            "g2g3",
        )
        assert stockfish.get_parameters()["UCI_Elo"] == 2000

        stockfish.set_elo_rating(1350)
        assert stockfish.get_best_move() in (
            "d1e2",
            "b1c3",
            "d2d3",
            "d2d4",
        )
        assert stockfish.get_parameters()["UCI_Elo"] == 1350

    def test_stockfish_constructor_with_custom_params(self):
        stockfish = Stockfish(parameters={"Skill Level": 1})
        assert stockfish.get_parameters() == {
            "Write Debug Log": "false",
            "Contempt": 0,
            "Min Split Depth": 0,
            "Threads": 1,
            "Ponder": "false",
            "Hash": 16,
            "MultiPV": 1,
            "Skill Level": 1,
            "Move Overhead": 30,
            "Minimum Thinking Time": 20,
            "Slow Mover": 80,
            "UCI_Chess960": "false",
            "UCI_LimitStrength": "false",
            "UCI_Elo": 1350,
        }

    def test_get_board_visual(self, stockfish):
        stockfish.set_position(["e2e4", "e7e6", "d2d4", "d7d5"])
        expected_result = (
            "+---+---+---+---+---+---+---+---+\n"
            "| r | n | b | q | k | b | n | r |\n"
            "+---+---+---+---+---+---+---+---+\n"
            "| p | p | p |   |   | p | p | p |\n"
            "+---+---+---+---+---+---+---+---+\n"
            "|   |   |   |   | p |   |   |   |\n"
            "+---+---+---+---+---+---+---+---+\n"
            "|   |   |   | p |   |   |   |   |\n"
            "+---+---+---+---+---+---+---+---+\n"
            "|   |   |   | P | P |   |   |   |\n"
            "+---+---+---+---+---+---+---+---+\n"
            "|   |   |   |   |   |   |   |   |\n"
            "+---+---+---+---+---+---+---+---+\n"
            "| P | P | P |   |   | P | P | P |\n"
            "+---+---+---+---+---+---+---+---+\n"
            "| R | N | B | Q | K | B | N | R |\n"
            "+---+---+---+---+---+---+---+---+\n"
        )
        assert stockfish.get_board_visual() == expected_result

    def test_get_fen_position(self, stockfish):
        assert (
            stockfish.get_fen_position()
            == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )

    def test_get_fen_position_after_some_moves(self, stockfish):
        stockfish.set_position(["e2e4", "e7e6"])
        assert (
            stockfish.get_fen_position()
            == "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
        )

    def test_get_stockfish_major_version(self, stockfish):
        assert stockfish.get_stockfish_major_version() in (
            8,
            9,
            10,
            11,
            12,
            13,
        )

    def test_get_evaluation_cp(self, stockfish):
        stockfish.set_fen_position(
            "r4rk1/pppb1p1p/2nbpqp1/8/3P4/3QBN2/PPP1BPPP/R4RK1 w - - 0 11"
        )
        evaluation = stockfish.get_evaluation()
        assert evaluation["type"] == "cp" and evaluation["value"] > 0

    def test_get_evaluation_checkmate(self, stockfish):
        stockfish.set_fen_position("1nb1k1n1/pppppppp/8/6r1/5bqK/6r1/8/8 w - - 2 2")
        assert stockfish.get_evaluation() == {"type": "mate", "value": 0}

    def test_get_evaluation_stalemate(self, stockfish):
        stockfish.set_fen_position("1nb1kqn1/pppppppp/8/6r1/5b1K/6r1/8/8 w - - 2 2")
        assert stockfish.get_evaluation() == {"type": "cp", "value": 0}

    def test_set_depth(self, stockfish):
        stockfish.set_depth(12)
        assert stockfish.depth == "12"
        stockfish.get_best_move()
        assert "depth 12" in stockfish.info

    def test_get_best_move_wrong_position(self):
        wrong_fen = "3kk3/8/8/8/8/8/8/3KK3 w - - 0 0"
        s = Stockfish()
        s.set_fen_position(wrong_fen)
        assert s.get_best_move() in (
            "d1e2",
            "d1c1",
        )

    def test_get_parameters(self):
        s1 = Stockfish()
        s2 = Stockfish()
        arg1 = s1.get_parameters()
        arg2 = s2.get_parameters()
        assert arg1 == arg2
        s1.set_skill_level(1)
        arg1 = s1.get_parameters()
        arg2 = s2.get_parameters()
        assert arg1 != arg2

    def test_get_top_moves(self):
        stockfish = Stockfish(depth=15, parameters={"MultiPV": 4})
        stockfish.set_fen_position("1rQ1r1k1/5ppp/8/8/1R6/8/2r2PPP/4R1K1 w - - 0 1")
        assert stockfish.get_top_moves(2) == [
            {"Move": "e1e8", "Centipawn": None, "Mate": 1},
            {"Move": "c8e8", "Centipawn": None, "Mate": 2},
        ]
        stockfish.set_fen_position("8/8/8/8/8/3r2k1/8/6K1 w - - 0 1")
        assert stockfish.get_top_moves(2) == [
            {"Move": "g1f1", "Centipawn": None, "Mate": -2},
            {"Move": "g1h1", "Centipawn": None, "Mate": -1},
        ]

    def test_get_top_moves_mate(self):
        stockfish = Stockfish(depth=10, parameters={"MultiPV": 3})
        stockfish.set_fen_position("8/8/8/8/8/6k1/8/3r2K1 w - - 0 1")
        assert stockfish.get_top_moves() == []
        assert stockfish.get_parameters()["MultiPV"] == 3

    def test_get_top_moves_raising_error(self):
        stockfish = Stockfish()
        stockfish.set_fen_position(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )
        with pytest.raises(ValueError):
            stockfish.get_top_moves(0)
        assert len(stockfish.get_top_moves(2)) == 2
        assert stockfish.get_parameters()["MultiPV"] == 1

    def test_make_moves_from_current_position(self):
        stockfish = Stockfish()
        stockfish.set_fen_position(
            "r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1"
        )
        with pytest.raises(ValueError):
            stockfish.make_moves_from_current_position([])
        stockfish.make_moves_from_current_position(["e1g1"])
        assert (
            stockfish.get_fen_position()
            == "r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 1 1"
        )
        stockfish.make_moves_from_current_position(
            ["f6e4", "d2d4", "e4d6", "b5c6", "d7c6", "d4e5", "d6f5"]
        )
        assert (
            stockfish.get_fen_position()
            == "r1bqkb1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNBQ1RK1 w kq - 1 5"
        )
        stockfish.make_moves_from_current_position(
            ["d1d8", "e8d8", "b1c3", "d8e8", "f1d1", "f5e7", "h2h3", "f7f5"]
        )
        assert (
            stockfish.get_fen_position()
            == "r1b1kb1r/ppp1n1pp/2p5/4Pp2/8/2N2N1P/PPP2PP1/R1BR2K1 w - f6 0 9"
        )
