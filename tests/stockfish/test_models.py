import pytest
from timeit import default_timer
import time
from typing import Optional, List

from stockfish import Stockfish, StockfishException


class TestStockfish:
    @pytest.fixture
    def stockfish(self) -> Stockfish:
        return Stockfish()

    def test_constructor_defaults(self):
        sf = Stockfish()
        assert sf is not None
        assert sf._path == "stockfish"
        assert sf._parameters == sf._DEFAULT_STOCKFISH_PARAMS
        assert sf._depth == 15
        assert sf._num_nodes == 1000000
        assert sf._turn_perspective is True

    def test_constructor_options(self):
        sf = Stockfish(
            depth=20,
            num_nodes=1000,
            turn_perspective=False,
            parameters={"Threads": 2, "UCI_Elo": 1500},
        )
        assert sf._depth == 20
        assert sf._num_nodes == 1000
        assert sf._turn_perspective is False
        assert sf._parameters["Threads"] == 2
        assert sf._parameters["UCI_Elo"] == 1500

    @pytest.mark.parametrize(
        "parameters",
        [{"depth": "20"}, {"num_nodes": "100"}, {"turn_perspective": "False"}],
    )
    def test_constructor_raises_type_errors(self, parameters):
        with pytest.raises(TypeError):
            Stockfish(**parameters)

    def test_get_best_move_first_move(self, stockfish: Stockfish):
        best_move = stockfish.get_best_move()
        assert best_move in ("e2e3", "e2e4", "g1f3", "b1c3", "d2d4")

    def test_get_best_move_time_first_move(self, stockfish: Stockfish):
        best_move = stockfish.get_best_move_time(1000)
        assert best_move in ("e2e3", "e2e4", "g1f3", "b1c3", "d2d4")

    @pytest.mark.slow
    def test_get_best_move_remaining_time_first_move(self, stockfish: Stockfish):
        best_move = stockfish.get_best_move(wtime=1000)
        assert best_move in ("a2a3", "d2d4", "e2e4", "g1f3", "c2c4")
        best_move = stockfish.get_best_move(btime=1000)
        assert best_move in ("g1f3", "d2d4", "e2e4", "c2c4")
        best_move = stockfish.get_best_move(wtime=1000, btime=1000)
        assert best_move in ("g2g3", "g1f3", "e2e4", "d2d4", "c2c4", "e2e3")
        best_move = stockfish.get_best_move(wtime=5 * 60 * 1000, btime=1000)
        assert best_move in ("e2e3", "e2e4", "g1f3", "b1c3", "d2d4")

    def test_set_position_resets_info(self, stockfish: Stockfish):
        stockfish.set_position(["e2e4", "e7e6"])
        stockfish.get_best_move()
        assert stockfish.info != ""
        stockfish.set_position(["e2e4", "e7e6"])
        assert stockfish.info == ""

    def test_get_best_move_not_first_move(self, stockfish: Stockfish):
        stockfish.set_position(["e2e4", "e7e6"])
        best_move = stockfish.get_best_move()
        assert best_move in ("d2d4", "g1f3")

    def test_get_best_move_time_not_first_move(self, stockfish: Stockfish):
        stockfish.set_position(["e2e4", "e7e6"])
        best_move = stockfish.get_best_move_time(1000)
        assert best_move in ("d2d4", "g1f3")

    @pytest.mark.slow
    def test_get_best_move_remaining_time_not_first_move(self, stockfish: Stockfish):
        stockfish.set_position(["e2e4", "e7e6"])
        best_move = stockfish.get_best_move(wtime=1000)
        assert best_move in ("d2d4", "a2a3", "d1e2", "b1c3")
        best_move = stockfish.get_best_move(btime=1000)
        assert best_move in ("d2d4", "b1c3")
        best_move = stockfish.get_best_move(wtime=1000, btime=1000)
        assert best_move in ("d2d4", "b1c3", "g1f3")
        best_move = stockfish.get_best_move(wtime=5 * 60 * 1000, btime=1000)
        assert best_move in ("e2e3", "e2e4", "g1f3", "b1c3", "d2d4")

    def test_get_best_move_checkmate(self, stockfish: Stockfish):
        stockfish.set_position(["f2f3", "e7e5", "g2g4", "d8h4"])
        assert stockfish.get_best_move() is None

    def test_get_best_move_time_checkmate(self, stockfish: Stockfish):
        stockfish.set_position(["f2f3", "e7e5", "g2g4", "d8h4"])
        assert stockfish.get_best_move_time(1000) is None

    def test_get_best_move_remaining_time_checkmate(self, stockfish: Stockfish):
        stockfish.set_position(["f2f3", "e7e5", "g2g4", "d8h4"])
        assert stockfish.get_best_move(wtime=1000) is None
        assert stockfish.get_best_move(btime=1000) is None
        assert stockfish.get_best_move(wtime=1000, btime=1000) is None
        assert stockfish.get_best_move(wtime=5 * 60 * 1000, btime=1000) is None

    def test_set_fen_position(self, stockfish: Stockfish):
        stockfish.set_fen_position(
            "7r/1pr1kppb/2n1p2p/2NpP2P/5PP1/1P6/P6K/R1R2B2 w - - 1 27"
        )
        assert stockfish.is_move_correct("f4f5") is True
        assert stockfish.is_move_correct("a1c1") is False

    def test_castling(self, stockfish: Stockfish):
        assert stockfish.is_move_correct("e1g1") is False
        stockfish.set_fen_position(
            "rnbqkbnr/ppp3pp/3ppp2/8/4P3/5N2/PPPPBPPP/RNBQK2R w KQkq - 0 4"
        )
        assert stockfish.is_move_correct("e1g1") is True

    def test_set_fen_position_mate(self, stockfish: Stockfish):
        stockfish.set_fen_position("8/8/8/6pp/8/4k1PP/8/r3K3 w - - 12 53")
        assert stockfish.get_best_move() is None
        assert stockfish.info == "info depth 0 score mate 0"

    def test_clear_info_after_set_new_fen_position(self, stockfish: Stockfish):
        stockfish.set_fen_position("8/8/8/6pp/8/4k1PP/r7/4K3 b - - 11 52")
        stockfish.get_best_move()
        stockfish.set_fen_position("8/8/8/6pp/8/4k1PP/8/r3K3 w - - 12 53")
        assert stockfish.info == ""

        stockfish.set_fen_position("8/8/8/6pp/8/4k1PP/r7/4K3 b - - 11 52")
        stockfish.get_best_move()
        stockfish.set_fen_position("8/8/8/6pp/8/4k1PP/8/r3K3 w - - 12 53")
        assert stockfish.info == ""

    def test_set_fen_position_starts_new_game(self, stockfish: Stockfish):
        stockfish.set_fen_position(
            "7r/1pr1kppb/2n1p2p/2NpP2P/5PP1/1P6/P6K/R1R2B2 w - - 1 27"
        )
        stockfish.get_best_move()
        assert stockfish.info != ""
        stockfish.set_fen_position("3kn3/p5rp/1p3p2/3B4/3P1P2/2P5/1P3K2/8 w - - 0 53")
        assert stockfish.info == ""

    def test_set_fen_position_ucinewgame(self, stockfish: Stockfish):
        stockfish.set_depth(16)
        stockfish.send_ucinewgame_command()
        stockfish.set_fen_position(
            "rnbqk2r/pppp1ppp/3bpn2/8/3PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 1"
        )
        assert stockfish.get_best_move() == "e4e5"

        stockfish.set_fen_position(
            "rnbqk2r/pppp1ppp/3bpn2/4P3/3P4/2N5/PPP2PPP/R1BQKBNR b KQkq - 0 1"
        )
        assert stockfish.get_best_move() == "d6e7"

        stockfish.set_fen_position(
            "rnbqk2r/pppp1ppp/3bpn2/8/3PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 1"
        )
        assert stockfish.get_best_move() == "e4e5"

    def test_is_move_correct_first_move(self, stockfish: Stockfish):
        assert stockfish.is_move_correct("e2e1") is False
        assert stockfish.is_move_correct("a2a3") is True

    def test_is_move_correct_not_first_move(self, stockfish: Stockfish):
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
    def test_last_info(self, stockfish: Stockfish, value):
        stockfish.set_fen_position("r6k/6b1/2b1Q3/p6p/1p5q/3P2PP/5r1K/8 w - - 1 31")
        stockfish.get_best_move()
        assert value in stockfish.info

    def test_set_skill_level(self, stockfish: Stockfish):
        stockfish.set_fen_position(
            "rnbqkbnr/ppp2ppp/3pp3/8/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1"
        )

        assert stockfish.get_engine_parameters()["Skill Level"] == 20

        stockfish.set_skill_level(1)
        assert stockfish.get_best_move() in (
            "b2b3",
            "d2d3",
            "d2d4",
            "b1c3",
            "d1e2",
            "g2g3",
            "c2c4",
            "f1e2",
            "c2c3",
            "h2h3",
        )
        assert stockfish.get_engine_parameters()["Skill Level"] == 1
        assert stockfish.get_engine_parameters()["UCI_LimitStrength"] == False
        assert stockfish._on_weaker_setting()

        stockfish.set_skill_level(20)
        assert stockfish.get_best_move() in ("d2d4", "c2c4")
        assert stockfish.get_engine_parameters()["Skill Level"] == 20
        assert stockfish.get_engine_parameters()["UCI_LimitStrength"] == False
        assert not stockfish._on_weaker_setting()

    def test_set_elo_rating(self, stockfish: Stockfish):
        stockfish.set_fen_position(
            "rnbqkbnr/ppp2ppp/3pp3/8/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1"
        )

        assert stockfish.get_engine_parameters()["UCI_Elo"] == 1350
        assert not stockfish._on_weaker_setting()

        stockfish.set_elo_rating(2000)
        assert stockfish.get_best_move() in (
            "d2d4",
            "b1c3",
            "d1e2",
            "c2c4",
            "f1e2",
            "h2h3",
            "c2c3",
            "f1d3",
            "a2a3",
        )
        assert stockfish.get_engine_parameters()["UCI_Elo"] == 2000
        assert stockfish.get_engine_parameters()["UCI_LimitStrength"] == True
        assert stockfish._on_weaker_setting()

        stockfish.set_elo_rating(1350)
        assert stockfish.get_best_move() in (
            "d1e2",
            "b1c3",
            "d2d3",
            "d2d4",
            "c2c4",
            "f1e2",
            "c2c3",
            "f1b5",
            "g2g3",
            "h2h3",
        )
        assert stockfish.get_engine_parameters()["UCI_Elo"] == 1350
        assert stockfish.get_engine_parameters()["UCI_LimitStrength"] == True
        assert stockfish._on_weaker_setting()

        stockfish.set_elo_rating(2850)
        major_version = stockfish.get_stockfish_major_version()

        expected_best_moves = ["d2d4", "b1c3", "c2c3", "c2c4", "f1b5", "f1e2"]
        if major_version >= 12 and not stockfish.is_development_build_of_engine():
            expected_best_moves.remove("f1e2")

        assert stockfish.get_best_move() in expected_best_moves

        assert stockfish.get_engine_parameters()["UCI_Elo"] == 2850
        assert stockfish._on_weaker_setting()

    @pytest.mark.slow
    def test_resume_full_strength(self, stockfish: Stockfish):
        stockfish.set_fen_position(
            "1r1qrbk1/2pb1pp1/p4n1p/P3P3/3P4/NB4BP/6P1/R2QR1K1 b - - 0 1"
        )
        stockfish.set_depth(13)
        stockfish.set_elo_rating(1350)
        assert stockfish._on_weaker_setting()
        best_moves = ["d7c6", "d7f5"]
        low_elo_moves = [stockfish.get_best_move() for _ in range(15)]
        assert not all(x in best_moves for x in low_elo_moves)
        stockfish.set_skill_level(1)
        assert stockfish._on_weaker_setting()
        low_skill_level_moves = [stockfish.get_best_move() for _ in range(15)]
        assert not all(x in best_moves for x in low_skill_level_moves)
        stockfish.resume_full_strength()
        assert not stockfish._on_weaker_setting()
        full_strength_moves = [stockfish.get_best_move() for _ in range(15)]
        assert all(x in best_moves for x in full_strength_moves)

    def test_specific_params(self, stockfish: Stockfish):
        old_parameters = {
            "Debug Log File": "",
            "Contempt": 0,
            "Min Split Depth": 0,
            "Threads": 1,
            "Ponder": False,
            "Hash": 16,
            "MultiPV": 1,
            "Skill Level": 20,
            "Move Overhead": 10,
            "Minimum Thinking Time": 20,
            "Slow Mover": 100,
            "UCI_Chess960": False,
            "UCI_LimitStrength": False,
            "UCI_Elo": 1350,
        }
        expected_parameters = old_parameters.copy()
        stockfish.set_skill_level(1)
        expected_parameters["Skill Level"] = 1
        assert stockfish.get_engine_parameters() == expected_parameters
        assert stockfish._DEFAULT_STOCKFISH_PARAMS == old_parameters
        stockfish.set_skill_level(20)
        expected_parameters["Skill Level"] = 20
        assert stockfish.get_engine_parameters() == old_parameters
        assert stockfish._DEFAULT_STOCKFISH_PARAMS == old_parameters

        stockfish.update_engine_parameters({"Threads": 4})
        expected_parameters["Threads"] = 4
        assert stockfish.get_engine_parameters() == expected_parameters
        stockfish.update_engine_parameters({"Hash": 128})
        expected_parameters["Hash"] = 128
        assert stockfish.get_engine_parameters() == expected_parameters
        stockfish.update_engine_parameters({"Hash": 256, "Threads": 3})
        expected_parameters.update({"Hash": 256, "Threads": 3})
        assert stockfish.get_engine_parameters() == expected_parameters

    @pytest.mark.parametrize(
        "parameters",
        [
            {"Ponder": "true"},
            {"Ponder": "false"},
            {"UCI_LimitStrength": "true"},
            {"UCI_LimitStrength": "false"},
            {"UCI_Chess960": "true"},
            {"UCI_Chess960": "false"},
        ],
    )
    def test_update_engine_parameters_wrong_type(
        self, stockfish: Stockfish, parameters
    ):
        with pytest.raises(ValueError):
            stockfish.update_engine_parameters(parameters)

    def test_deprecated_get_parameters(self, stockfish: Stockfish):
        with pytest.raises(ValueError):
            stockfish.get_parameters()

    def test_chess960_position(self, stockfish: Stockfish):
        assert "KQkq" in stockfish.get_fen_position()
        old_parameters = stockfish.get_engine_parameters()
        expected_parameters = stockfish.get_engine_parameters()
        expected_parameters["UCI_Chess960"] = True
        stockfish.update_engine_parameters({"UCI_Chess960": True})
        assert "HAha" in stockfish.get_fen_position()
        assert stockfish.get_engine_parameters() == expected_parameters
        stockfish.set_fen_position("4rkr1/4p1p1/8/8/8/8/8/4nK1R w K - 0 100")
        assert stockfish.get_best_move() == "f1h1"
        stockfish.set_turn_perspective(False)
        assert stockfish.get_evaluation() == {"type": "mate", "value": 2}
        stockfish.set_turn_perspective()
        assert stockfish.get_evaluation() == {"type": "mate", "value": 2}
        assert stockfish.will_move_be_a_capture("f1h1") is Stockfish.Capture.NO_CAPTURE
        assert (
            stockfish.will_move_be_a_capture("f1e1") is Stockfish.Capture.DIRECT_CAPTURE
        )
        stockfish.update_engine_parameters({"UCI_Chess960": False})
        assert stockfish.get_engine_parameters() == old_parameters
        assert stockfish.get_best_move() == "f1g1"
        stockfish.set_turn_perspective(False)
        assert stockfish.get_evaluation() == {"type": "mate", "value": 2}
        stockfish.set_turn_perspective()
        assert stockfish.get_evaluation() == {"type": "mate", "value": 2}
        assert stockfish.will_move_be_a_capture("f1g1") is Stockfish.Capture.NO_CAPTURE

    def test_get_board_visual_white(self, stockfish: Stockfish):
        stockfish.set_position(["e2e4", "e7e6", "d2d4", "d7d5"])
        if stockfish.get_stockfish_major_version() >= 12:
            expected_result = (
                "+---+---+---+---+---+---+---+---+\n"
                "| r | n | b | q | k | b | n | r | 8\n"
                "+---+---+---+---+---+---+---+---+\n"
                "| p | p | p |   |   | p | p | p | 7\n"
                "+---+---+---+---+---+---+---+---+\n"
                "|   |   |   |   | p |   |   |   | 6\n"
                "+---+---+---+---+---+---+---+---+\n"
                "|   |   |   | p |   |   |   |   | 5\n"
                "+---+---+---+---+---+---+---+---+\n"
                "|   |   |   | P | P |   |   |   | 4\n"
                "+---+---+---+---+---+---+---+---+\n"
                "|   |   |   |   |   |   |   |   | 3\n"
                "+---+---+---+---+---+---+---+---+\n"
                "| P | P | P |   |   | P | P | P | 2\n"
                "+---+---+---+---+---+---+---+---+\n"
                "| R | N | B | Q | K | B | N | R | 1\n"
                "+---+---+---+---+---+---+---+---+\n"
                "  a   b   c   d   e   f   g   h\n"
            )
        else:
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

        stockfish._put("d")
        stockfish._read_line()  # skip a line
        assert "+---+---+---+" in stockfish._read_line()
        # Tests that the previous call to get_board_visual left no remaining lines to be read. This means
        # the second line read after stockfish._put("d") now will be the +---+---+---+ of the new outputted board.

    def test_get_board_visual_black(self, stockfish: Stockfish):
        stockfish.set_position(["e2e4", "e7e6", "d2d4", "d7d5"])
        if stockfish.get_stockfish_major_version() >= 12:
            expected_result = (
                "+---+---+---+---+---+---+---+---+\n"
                "| R | N | B | K | Q | B | N | R | 1\n"
                "+---+---+---+---+---+---+---+---+\n"
                "| P | P | P |   |   | P | P | P | 2\n"
                "+---+---+---+---+---+---+---+---+\n"
                "|   |   |   |   |   |   |   |   | 3\n"
                "+---+---+---+---+---+---+---+---+\n"
                "|   |   |   | P | P |   |   |   | 4\n"
                "+---+---+---+---+---+---+---+---+\n"
                "|   |   |   |   | p |   |   |   | 5\n"
                "+---+---+---+---+---+---+---+---+\n"
                "|   |   |   | p |   |   |   |   | 6\n"
                "+---+---+---+---+---+---+---+---+\n"
                "| p | p | p |   |   | p | p | p | 7\n"
                "+---+---+---+---+---+---+---+---+\n"
                "| r | n | b | k | q | b | n | r | 8\n"
                "+---+---+---+---+---+---+---+---+\n"
                "  h   g   f   e   d   c   b   a\n"
            )
        else:
            expected_result = (
                "+---+---+---+---+---+---+---+---+\n"
                "| R | N | B | K | Q | B | N | R |\n"
                "+---+---+---+---+---+---+---+---+\n"
                "| P | P | P |   |   | P | P | P |\n"
                "+---+---+---+---+---+---+---+---+\n"
                "|   |   |   |   |   |   |   |   |\n"
                "+---+---+---+---+---+---+---+---+\n"
                "|   |   |   | P | P |   |   |   |\n"
                "+---+---+---+---+---+---+---+---+\n"
                "|   |   |   |   | p |   |   |   |\n"
                "+---+---+---+---+---+---+---+---+\n"
                "|   |   |   | p |   |   |   |   |\n"
                "+---+---+---+---+---+---+---+---+\n"
                "| p | p | p |   |   | p | p | p |\n"
                "+---+---+---+---+---+---+---+---+\n"
                "| r | n | b | k | q | b | n | r |\n"
                "+---+---+---+---+---+---+---+---+\n"
            )

        assert stockfish.get_board_visual(False) == expected_result

        stockfish._put("d")
        stockfish._read_line()  # skip a line
        assert "+---+---+---+" in stockfish._read_line()
        # Tests that the previous call to get_board_visual left no remaining lines to be read. This means
        # the second line read after stockfish._put("d") now will be the +---+---+---+ of the new outputted board.

    def test_get_fen_position(self, stockfish: Stockfish):
        assert (
            stockfish.get_fen_position()
            == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )
        stockfish._put("d")
        stockfish._read_line()  # skip a line
        assert "+---+---+---+" in stockfish._read_line()

    def test_get_fen_position_after_some_moves(self, stockfish: Stockfish):
        stockfish.set_position(["e2e4", "e7e6"])
        assert (
            stockfish.get_fen_position()
            == "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
        )

    def test_get_stockfish_major_version(self, stockfish: Stockfish):
        assert (
            stockfish.get_stockfish_major_version() in (8, 9, 10, 11, 12, 13, 14, 15)
        ) != stockfish.is_development_build_of_engine()

    @pytest.mark.slow
    def test_get_evaluation_cp(self, stockfish: Stockfish):
        stockfish.set_depth(20)
        stockfish.set_fen_position(
            "r4rk1/pppb1p1p/2nbpqp1/8/3P4/3QBN2/PPP1BPPP/R4RK1 w - - 0 11"
        )
        evaluation = stockfish.get_evaluation()
        assert (
            evaluation["type"] == "cp"
            and evaluation["value"] >= 60
            and evaluation["value"] <= 150
        )
        stockfish.set_skill_level(1)
        with pytest.warns(UserWarning):
            evaluation = stockfish.get_evaluation()
        assert (
            evaluation["type"] == "cp"
            and evaluation["value"] >= 60
            and evaluation["value"] <= 150
        )

    def test_get_evaluation_checkmate(self, stockfish: Stockfish):
        stockfish.set_fen_position("1nb1k1n1/pppppppp/8/6r1/5bqK/6r1/8/8 w - - 2 2")
        assert stockfish.get_evaluation() == {"type": "mate", "value": 0}

    def test_get_evaluation_stalemate(self, stockfish: Stockfish):
        stockfish.set_fen_position("1nb1kqn1/pppppppp/8/6r1/5b1K/6r1/8/8 w - - 2 2")
        assert stockfish.get_evaluation() == {"type": "cp", "value": 0}
        stockfish.set_turn_perspective(not stockfish.get_turn_perspective())
        assert stockfish.get_evaluation() == {"type": "cp", "value": 0}

    def test_get_static_eval(self, stockfish: Stockfish):
        stockfish.set_turn_perspective(False)
        stockfish.set_fen_position("r7/8/8/8/8/5k2/4p3/4K3 w - - 0 1")
        static_eval_1 = stockfish.get_static_eval()
        assert isinstance(static_eval_1, float) and static_eval_1 < -3
        stockfish.set_fen_position("r7/8/8/8/8/5k2/4p3/4K3 b - - 0 1")
        static_eval_2 = stockfish.get_static_eval()
        assert isinstance(static_eval_2, float) and static_eval_2 < -3
        stockfish.set_turn_perspective()
        static_eval_3 = stockfish.get_static_eval()
        assert isinstance(static_eval_3, float) and static_eval_3 > 3
        stockfish.set_fen_position("r7/8/8/8/8/5k2/4p3/4K3 w - - 0 1")
        static_eval_4 = stockfish.get_static_eval()
        assert isinstance(static_eval_4, float) and static_eval_4 < -3
        if stockfish.get_stockfish_major_version() >= 12:
            stockfish.set_fen_position("8/8/8/8/8/4k3/4p3/r3K3 w - - 0 1")
            assert stockfish.get_static_eval() is None

    def test_set_depth(self, stockfish: Stockfish):
        stockfish.set_depth(12)
        assert stockfish._depth == 12
        stockfish.get_best_move()
        assert "depth 12" in stockfish.info
        stockfish.set_depth()
        assert stockfish._depth == 15
        stockfish.get_best_move()
        assert "depth 15" in stockfish.info

    @pytest.mark.parametrize("depth", ["12", True, 12.1, 0, None])
    def test_set_depth_raises_type_error(self, stockfish: Stockfish, depth):
        with pytest.raises(TypeError):
            stockfish.set_depth(depth)

    def test_get_depth(self, stockfish: Stockfish):
        stockfish.set_depth(12)
        assert stockfish.get_depth() == 12
        assert stockfish._depth == 12
        stockfish.set_depth(20)
        assert stockfish.get_depth() == 20
        assert stockfish._depth == 20

    def test_set_num_nodes(self, stockfish: Stockfish):
        stockfish.set_num_nodes(100)
        assert stockfish._num_nodes == 100
        stockfish.set_num_nodes()
        assert stockfish._num_nodes == 1000000

    @pytest.mark.parametrize("num_nodes", ["100", 100.1, None, True])
    def test_set_num_nodes_raises_type_error(self, stockfish: Stockfish, num_nodes):
        with pytest.raises(TypeError):
            stockfish.set_num_nodes(num_nodes)

    def test_get_num_nodes(self, stockfish: Stockfish):
        stockfish.set_num_nodes(100)
        assert stockfish.get_num_nodes() == 100
        stockfish.set_num_nodes()
        assert stockfish.get_num_nodes() == 1000000

    def test_get_best_move_wrong_position(self, stockfish: Stockfish):
        stockfish.set_depth(2)
        wrong_fen = "3kk3/8/8/8/8/8/8/3KK3 w - - 0 0"
        stockfish.set_fen_position(wrong_fen)
        assert stockfish.get_best_move() in ("d1e2", "d1c1", "d1c2")

    def test_constructor(self, stockfish: Stockfish):
        # Will also use a new stockfish instance in order to test sending
        # params to the constructor.

        stockfish_2 = Stockfish(
            depth=16, parameters={"MultiPV": 2, "UCI_Elo": 2850, "UCI_Chess960": True}
        )
        assert (
            stockfish_2.get_fen_position()
            == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w HAha - 0 1"
        )
        assert (
            stockfish.get_fen_position()
            == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )

        stockfish_2.get_best_move()
        stockfish.get_best_move()
        assert "multipv 2" in stockfish_2.info
        assert "depth 16" in stockfish_2.info
        assert stockfish_2._depth == 16
        assert "multipv 1" in stockfish.info
        assert "depth 15" in stockfish.info
        assert stockfish._depth == 15

        stockfish_1_params = stockfish.get_engine_parameters()
        stockfish_2_params = stockfish_2.get_engine_parameters()
        for key in stockfish_2_params.keys():
            if key == "MultiPV":
                assert stockfish_2_params[key] == 2
                assert stockfish_1_params[key] == 1
            elif key == "UCI_Elo":
                assert stockfish_2_params[key] == 2850
                assert stockfish_1_params[key] == 1350
            elif key == "UCI_LimitStrength":
                assert stockfish_2_params[key] == True
                assert stockfish_1_params[key] == False
            elif key == "UCI_Chess960":
                assert stockfish_2_params[key] == True
                assert stockfish_1_params[key] == False
            else:
                assert stockfish_2_params[key] == stockfish_1_params[key]

    def test_parameters_functions(self, stockfish: Stockfish):
        old_parameters = stockfish.get_engine_parameters()
        stockfish.set_fen_position("4rkr1/4p1p1/8/8/8/8/8/5K1R w H - 0 100")
        assert stockfish.get_best_move() == "f1g1"  # ensures Chess960 param is false.
        assert stockfish.get_fen_position() == "4rkr1/4p1p1/8/8/8/8/8/5K1R w K - 0 100"
        assert "multipv 1" in stockfish.info
        stockfish.update_engine_parameters(
            {
                "Minimum Thinking Time": 10,
                "Hash": 32,
                "MultiPV": 2,
                "UCI_Chess960": True,
            }
        )
        assert stockfish.get_fen_position() == "4rkr1/4p1p1/8/8/8/8/8/5K1R w H - 0 100"
        assert stockfish.get_best_move() == "f1h1"
        assert "multipv 2" in stockfish.info
        updated_parameters = stockfish.get_engine_parameters()
        for key, value in updated_parameters.items():
            if key == "Minimum Thinking Time":
                assert value == 10
            elif key == "Hash":
                assert value == 32
            elif key == "MultiPV":
                assert value == 2
            elif key == "UCI_Chess960":
                assert value == True
            else:
                assert updated_parameters[key] == old_parameters[key]
        assert stockfish.get_engine_parameters()["UCI_LimitStrength"] == False
        stockfish.update_engine_parameters({"UCI_Elo": 2000, "Skill Level": 19})
        assert stockfish.get_engine_parameters()["UCI_Elo"] == 2000
        assert stockfish.get_engine_parameters()["Skill Level"] == 19
        assert stockfish.get_engine_parameters()["UCI_LimitStrength"] == False
        stockfish.update_engine_parameters({"UCI_Elo": 2000})
        assert stockfish.get_engine_parameters()["UCI_LimitStrength"] == True
        stockfish.update_engine_parameters({"Skill Level": 20})
        assert stockfish.get_engine_parameters()["UCI_LimitStrength"] == False
        assert stockfish.get_fen_position() == "4rkr1/4p1p1/8/8/8/8/8/5K1R w H - 0 100"
        stockfish.reset_engine_parameters()
        assert stockfish.get_engine_parameters() == old_parameters
        assert stockfish.get_fen_position() == "4rkr1/4p1p1/8/8/8/8/8/5K1R w K - 0 100"
        with pytest.raises(ValueError):
            stockfish.update_engine_parameters({"Not an existing key", "value"})  # type: ignore

    def test_get_top_moves(self, stockfish: Stockfish):
        stockfish.set_depth(15)
        stockfish._set_option("MultiPV", 4)
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
        stockfish.set_elo_rating()
        with pytest.warns(UserWarning):
            top_moves = stockfish.get_top_moves(2)
        assert top_moves == [
            {"Move": "g1f1", "Centipawn": None, "Mate": -2},
            {"Move": "g1h1", "Centipawn": None, "Mate": -1},
        ]

    def test_get_top_moves_mate(self, stockfish: Stockfish):
        stockfish.set_depth(10)
        stockfish._set_option("MultiPV", 3)
        stockfish.set_fen_position("8/8/8/8/8/6k1/8/3r2K1 w - - 0 1")
        assert stockfish.get_top_moves() == []
        assert stockfish.get_engine_parameters()["MultiPV"] == 3

    def test_get_top_moves_verbose(self, stockfish: Stockfish):
        stockfish.set_depth(15)
        stockfish.set_fen_position("1rQ1r1k1/5ppp/8/8/1R6/8/2r2PPP/4R1K1 w - - 0 1")
        assert stockfish.get_top_moves(2, verbose=False) == [
            {"Move": "e1e8", "Centipawn": None, "Mate": 1},
            {"Move": "c8e8", "Centipawn": None, "Mate": 2},
        ]
        moves = stockfish.get_top_moves(2, verbose=True)
        assert all(
            k in moves[0]
            for k in (
                "Move",
                "Centipawn",
                "Mate",
                "MultiPVLine",
                "NodesPerSecond",
                "Nodes",
                "SelectiveDepth",
                "Time",
            )
        )
        if stockfish.does_current_engine_version_have_wdl_option():
            assert "WDL" in moves[0]

    def test_get_top_moves_num_nodes(self, stockfish: Stockfish):
        stockfish.set_fen_position("8/2q2pk1/4b3/1p6/7P/Q1p3P1/2B2P2/6K1 b - - 3 50")
        moves = stockfish.get_top_moves(2, num_nodes=1000000, verbose=True)
        assert int(moves[0]["Nodes"]) >= 1000000

    def test_get_top_moves_preserve_globals(self, stockfish: Stockfish):
        stockfish._set_option("MultiPV", 4)
        stockfish.set_num_nodes(2000000)
        stockfish.set_fen_position("1rQ1r1k1/5ppp/8/8/1R6/8/2r2PPP/4R1K1 w - - 0 1")
        stockfish.get_top_moves(2, num_nodes=100000)
        assert stockfish.get_num_nodes() == 2000000
        assert stockfish.get_engine_parameters()["MultiPV"] == 4

    def test_get_top_moves_raises_value_error(self, stockfish: Stockfish):
        stockfish.set_fen_position(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )
        with pytest.raises(ValueError):
            stockfish.get_top_moves(0)
        assert len(stockfish.get_top_moves(2)) == 2
        assert stockfish.get_engine_parameters()["MultiPV"] == 1

    def test_turn_perspective(self, stockfish: Stockfish):
        stockfish.set_depth(15)
        stockfish.set_fen_position("8/2q2pk1/4b3/1p6/7P/Q1p3P1/2B2P2/6K1 b - - 3 50")
        assert stockfish.get_turn_perspective()
        moves = stockfish.get_top_moves(1)
        assert moves[0]["Centipawn"] > 0
        assert stockfish.get_evaluation()["value"] > 0
        stockfish.set_turn_perspective(False)
        assert stockfish.get_turn_perspective() is False
        moves = stockfish.get_top_moves(1)
        assert moves[0]["Centipawn"] < 0
        assert stockfish.get_evaluation()["value"] < 0

    def test_turn_perspective_raises_type_error(self, stockfish: Stockfish):
        with pytest.raises(TypeError):
            stockfish.set_turn_perspective("not a bool")  # type: ignore

    def test_make_moves_from_current_position(self, stockfish: Stockfish):
        stockfish.set_fen_position(
            "r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1"
        )
        fen_1 = stockfish.get_fen_position()
        stockfish.make_moves_from_current_position([])
        assert fen_1 == stockfish.get_fen_position()

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

        stockfish.set_fen_position(
            "r1bqk2r/pppp1ppp/8/8/1b2n3/2N5/PPP2PPP/R1BQK2R w Qkq - 0 1"
        )

        invalid_moves = ["d1e3", "e1g1", "c3d5", "c1d4", "a7a6", "e1d2", "word"]

        for invalid_move in invalid_moves:
            with pytest.raises(ValueError):
                stockfish.make_moves_from_current_position([invalid_move])

    @pytest.mark.slow
    def test_make_moves_transposition_table_speed(self, stockfish: Stockfish):
        """
        Test if not sending the ucinewgame token allows SF to calculate a bit faster,
        since it can use data in its TT from previous calculations.
        """

        stockfish.set_depth(16)
        positions_considered = []
        stockfish.set_fen_position(
            "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq - 0 2"
        )

        total_time_calculating_first = 0.0
        for i in range(5):
            start = default_timer()
            chosen_move = stockfish.get_best_move()
            assert isinstance(chosen_move, str)
            total_time_calculating_first += default_timer() - start
            positions_considered.append(stockfish.get_fen_position())
            stockfish.make_moves_from_current_position([chosen_move])

        total_time_calculating_second = 0.0
        for i in range(len(positions_considered)):
            stockfish.send_ucinewgame_command()
            stockfish.set_fen_position(positions_considered[i])
            start = default_timer()
            stockfish.get_best_move()
            total_time_calculating_second += default_timer() - start

        assert total_time_calculating_first < total_time_calculating_second

    def test_get_wdl_stats(self, stockfish: Stockfish):
        stockfish.set_depth(15)
        stockfish._set_option("MultiPV", 2)
        if stockfish.does_current_engine_version_have_wdl_option():
            stockfish.get_wdl_stats()  # Testing that this doesn't raise a RuntimeError.
            stockfish.set_fen_position("7k/4R3/4P1pp/7N/8/8/1q5q/3K4 w - - 0 1")
            wdl_stats = stockfish.get_wdl_stats()
            assert isinstance(wdl_stats, list)
            assert wdl_stats[1] > wdl_stats[0] * 7
            assert abs(wdl_stats[0] - wdl_stats[2]) / wdl_stats[0] < 0.1

            stockfish.set_fen_position(
                "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            )
            wdl_stats_2 = stockfish.get_wdl_stats()
            assert isinstance(wdl_stats_2, list)
            assert wdl_stats_2[1] > wdl_stats_2[0] * 3.5
            assert wdl_stats_2[0] > wdl_stats_2[2] * 1.8

            stockfish.set_fen_position("8/8/8/8/8/6k1/6p1/6K1 w - - 0 1")
            assert stockfish.get_wdl_stats() is None

            stockfish.set_fen_position(
                "rnbqkb1r/pp3ppp/3p1n2/1B2p3/3NP3/2N5/PPP2PPP/R1BQK2R b KQkq - 0 6"
            )
            wdl_stats_3 = stockfish.get_wdl_stats()
            assert isinstance(wdl_stats_3, list) and len(wdl_stats_3) == 3

            stockfish.set_fen_position("8/8/8/8/8/3k4/3p4/3K4 w - - 0 1")
            assert stockfish.get_wdl_stats() is None

            stockfish.set_skill_level(1)
            with pytest.warns(UserWarning):
                stockfish.get_wdl_stats()
        else:
            with pytest.raises(RuntimeError):
                stockfish.get_wdl_stats()

    def test_does_current_engine_version_have_wdl_option(self, stockfish: Stockfish):
        if stockfish.get_stockfish_major_version() <= 11:
            assert not stockfish.does_current_engine_version_have_wdl_option()
            with pytest.raises(RuntimeError):
                stockfish.get_wdl_stats()

    @pytest.mark.slow
    def test_benchmark_result_with_defaults(self, stockfish: Stockfish):
        params = stockfish.BenchmarkParameters()
        result = stockfish.benchmark(params)
        # result should contain the last line of a successful method call
        assert result.split(" ")[0] == "Nodes/second"

    @pytest.mark.slow
    def test_benchmark_result_with_valid_options(self, stockfish: Stockfish):
        params = stockfish.BenchmarkParameters(
            ttSize=64, threads=2, limit=1000, limitType="movetime", evalType="classical"
        )
        result = stockfish.benchmark(params)
        # result should contain the last line of a successful method call
        assert result.split(" ")[0] == "Nodes/second"

    @pytest.mark.slow
    def test_benchmark_result_with_invalid_options(self, stockfish: Stockfish):
        params = stockfish.BenchmarkParameters(
            ttSize=2049,
            threads=0,
            limit=0,
            fenFile="./fakefile.fen",
            limitType="fghthtr",
            evalType="",
        )
        result = stockfish.benchmark(params)
        # result should contain the last line of a successful method call
        assert result.split(" ")[0] == "Nodes/second"

    @pytest.mark.slow
    def test_benchmark_result_with_invalid_type(self, stockfish: Stockfish):
        params = {
            "ttSize": 16,
            "threads": 1,
            "limit": 13,
            "fenFile": "./fakefile.fen",
            "limitType": "depth",
            "evalType": "mixed",
        }
        result = stockfish.benchmark(params)  # type: ignore
        # result should contain the last line of a successful method call
        assert result.split(" ")[0] == "Nodes/second"

    def test_multiple_calls_to_del(self, stockfish: Stockfish):
        assert stockfish._stockfish.poll() is None
        assert not stockfish._has_quit_command_been_sent
        stockfish.__del__()
        assert stockfish._stockfish.poll() is not None
        assert stockfish._has_quit_command_been_sent
        stockfish.__del__()
        assert stockfish._stockfish.poll() is not None
        assert stockfish._has_quit_command_been_sent

    def test_multiple_quit_commands(self, stockfish: Stockfish):
        # Test multiple quit commands, and include a call to del too. All of
        # them should run without causing some Exception.
        assert stockfish._stockfish.poll() is None
        assert not stockfish._has_quit_command_been_sent
        stockfish._put("quit")
        assert stockfish._has_quit_command_been_sent
        stockfish._put("quit")
        assert stockfish._has_quit_command_been_sent
        stockfish.__del__()
        assert stockfish._stockfish.poll() is not None
        assert stockfish._has_quit_command_been_sent
        stockfish._put(f"go depth {10}")
        # Should do nothing, and change neither of the values below.
        assert stockfish._stockfish.poll() is not None
        assert stockfish._has_quit_command_been_sent

    def test_what_is_on_square(self, stockfish: Stockfish):
        stockfish.set_fen_position(
            "rnbq1rk1/ppp1ppbp/5np1/3pP3/8/BPN5/P1PP1PPP/R2QKBNR w KQ d6 0 6"
        )
        assert stockfish.get_what_is_on_square("a1") is Stockfish.Piece.WHITE_ROOK
        assert stockfish.get_what_is_on_square("a8") is Stockfish.Piece.BLACK_ROOK
        assert stockfish.get_what_is_on_square("g8") is Stockfish.Piece.BLACK_KING
        assert stockfish.get_what_is_on_square("e1") is Stockfish.Piece.WHITE_KING
        assert stockfish.get_what_is_on_square("h2") is Stockfish.Piece.WHITE_PAWN
        assert stockfish.get_what_is_on_square("f8") is Stockfish.Piece.BLACK_ROOK
        assert stockfish.get_what_is_on_square("d6") is None
        assert stockfish.get_what_is_on_square("h7") is Stockfish.Piece.BLACK_PAWN
        assert stockfish.get_what_is_on_square("c3") is Stockfish.Piece.WHITE_KNIGHT
        assert stockfish.get_what_is_on_square("a3") is Stockfish.Piece.WHITE_BISHOP
        assert stockfish.get_what_is_on_square("h8") is None
        assert stockfish.get_what_is_on_square("d1") is Stockfish.Piece.WHITE_QUEEN
        assert stockfish.get_what_is_on_square("d4") is None
        assert stockfish.get_what_is_on_square("f6") is Stockfish.Piece.BLACK_KNIGHT
        assert stockfish.get_what_is_on_square("g7") is Stockfish.Piece.BLACK_BISHOP
        assert stockfish.get_what_is_on_square("d8") is Stockfish.Piece.BLACK_QUEEN
        with pytest.raises(ValueError):
            stockfish.get_what_is_on_square("i1")
        with pytest.raises(ValueError):
            stockfish.get_what_is_on_square("b9")

    def test_13_return_values_from_what_is_on_square(self, stockfish: Stockfish):
        stockfish.set_fen_position(
            "rnbq1rk1/ppp1ppbp/5np1/3pP3/8/BPN5/P1PP1PPP/R2QKBNR w KQ d6 0 6"
        )
        expected_enum_members = [
            "WHITE_PAWN",
            "BLACK_PAWN",
            "WHITE_KNIGHT",
            "BLACK_KNIGHT",
            "WHITE_BISHOP",
            "BLACK_BISHOP",
            "WHITE_ROOK",
            "BLACK_ROOK",
            "WHITE_QUEEN",
            "BLACK_QUEEN",
            "WHITE_KING",
            "BLACK_KING",
        ]
        rows = ["a", "b", "c", "d", "e", "f", "g", "h"]
        cols = ["1", "2", "3", "4", "5", "6", "7", "8"]
        for row in rows:
            for col in cols:
                val = stockfish.get_what_is_on_square(row + col)
                assert val is None or val.name in expected_enum_members

    def test_will_move_be_a_capture(self, stockfish: Stockfish):
        stockfish.set_fen_position(
            "1nbq1rk1/Ppp1ppbp/5np1/3pP3/8/BPN5/P1PP1PPP/R2QKBNR w KQ d6 0 6"
        )
        c3d5_result = stockfish.will_move_be_a_capture("c3d5")
        assert (
            c3d5_result is Stockfish.Capture.DIRECT_CAPTURE
            and c3d5_result.name == "DIRECT_CAPTURE"
            and c3d5_result.value == "direct capture"
        )
        e5d6_result = stockfish.will_move_be_a_capture("e5d6")
        assert (
            e5d6_result is Stockfish.Capture.EN_PASSANT
            and e5d6_result.name == "EN_PASSANT"
            and e5d6_result.value == "en passant"
        )
        f1e2_result = stockfish.will_move_be_a_capture("f1e2")
        assert (
            f1e2_result is Stockfish.Capture.NO_CAPTURE
            and f1e2_result.name == "NO_CAPTURE"
            and f1e2_result.value == "no capture"
        )
        e5f6_result = stockfish.will_move_be_a_capture("e5f6")
        assert (
            e5f6_result is Stockfish.Capture.DIRECT_CAPTURE
            and e5f6_result.name == "DIRECT_CAPTURE"
            and e5f6_result.value == "direct capture"
        )
        a3d6_result = stockfish.will_move_be_a_capture("a3d6")
        assert (
            a3d6_result is Stockfish.Capture.NO_CAPTURE
            and a3d6_result.name == "NO_CAPTURE"
            and a3d6_result.value == "no capture"
        )
        a7a8q_result = stockfish.will_move_be_a_capture("a7a8q")
        assert (
            a7a8q_result is Stockfish.Capture.NO_CAPTURE
            and a7a8q_result.name == "NO_CAPTURE"
            and a7a8q_result.value == "no capture"
        )
        a7a8b_result = stockfish.will_move_be_a_capture("a7a8b")
        assert (
            a7a8b_result is Stockfish.Capture.NO_CAPTURE
            and a7a8b_result.name == "NO_CAPTURE"
            and a7a8b_result.value == "no capture"
        )
        a7b8q_result = stockfish.will_move_be_a_capture("a7b8q")
        assert (
            a7b8q_result is Stockfish.Capture.DIRECT_CAPTURE
            and a7b8q_result.name == "DIRECT_CAPTURE"
            and a7b8q_result.value == "direct capture"
        )
        a7b8r_result = stockfish.will_move_be_a_capture("a7b8r")
        assert (
            a7b8r_result is Stockfish.Capture.DIRECT_CAPTURE
            and a7b8r_result.name == "DIRECT_CAPTURE"
            and a7b8r_result.value == "direct capture"
        )

        with pytest.raises(ValueError):
            stockfish.will_move_be_a_capture("c3c5")

    @pytest.mark.slow
    @pytest.mark.parametrize(
        "fen",
        [
            "2k2q2/8/8/8/8/8/8/2Q2K2 w - - 0 1",
            "1q2nB2/pP1k2KP/NN1Q1qP1/8/1P1p4/4p1br/3R4/6n1 w - - 0 1",
            "3rk1n1/ppp3pp/8/8/8/8/PPP5/1KR1R3 w - - 0 1",
        ],
    )
    def test_invalid_fen_king_attacked(self, stockfish: Stockfish, fen):
        # Each of these FENs have correct syntax, but
        # involve a king being attacked while it's the opponent's turn.
        old_del_counter = Stockfish._del_counter
        assert Stockfish._is_fen_syntax_valid(fen)
        if (
            fen == "8/8/8/3k4/3K4/8/8/8 b - - 0 1"
            and stockfish.get_stockfish_major_version() >= 14
        ):
            # Since for that FEN, SF 15 actually outputs a best move without crashing (unlike SF 14 and earlier).
            return
        if (
            fen == "2k2q2/8/8/8/8/8/8/2Q2K2 w - - 0 1"
            and stockfish.get_stockfish_major_version() >= 15
        ):
            # Development versions post SF 15 seem to output a bestmove for this fen.
            return
        assert not stockfish.is_fen_valid(fen)
        assert Stockfish._del_counter == old_del_counter + 2

        stockfish.set_fen_position(fen)
        with pytest.raises(StockfishException):
            stockfish.get_evaluation()

    @pytest.mark.slow
    def test_is_fen_valid(self, stockfish: Stockfish):
        old_params = stockfish.get_engine_parameters()
        old_info = stockfish.info
        old_depth = stockfish._depth
        old_fen = stockfish.get_fen_position()
        correct_fens: List[Optional[str]] = [
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "r1bQkb1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2RK1 b kq - 0 8",
            "4k3/8/4K3/8/8/8/8/8 w - - 10 50",
            "r1b1kb1r/ppp2ppp/3q4/8/P2Q4/8/1PP2PPP/RNB2RK1 w kq - 8 15",
            "4k3/8/4K3/8/8/8/8/8 w - - 99 50",
        ]
        correct_fens.extend([None] * 12)
        invalid_syntax_fens = [
            "r1bQkb1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2RK b kq - 0 8",
            "rnbqkb1r/pppp1ppp/4pn2/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 3",
            "rn1q1rk1/pbppbppp/1p2pn2/8/2PP4/5NP1/PP2PPBP/RNBQ1RK1 w w - 5 7",
            "4k3/8/4K3/71/8/8/8/8 w - - 10 50",
            "r1bQkb1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2R2 b kq - 0 8",
            "r1bQ1b1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2RK1 b kq - 0 8",
            "4k3/8/4K3/8/8/8/8/8 w - - 100 50",
            "4k3/8/4K3/8/8/8/8/8 w - - 101 50",
            "4k3/8/4K3/8/8/8/8/8 w - - -1 50",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0",
            "r1b1kb1r/ppp2ppp/3q4/8/P2Q4/8/1PP2PPP/RNB2RK1 w kq - - 8 15",
            "r1b1kb1r/ppp2ppp/3q4/8/P2Q4/8/1PP2PPP/RNB2RK1 w kq 8 15",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR W KQkq - 0 1",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR - KQkq - 0 1",
            "r1bQkb1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2RK1 b kq - - 8",
            "r1bQkb1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2RK1 b kq - 0 -",
            "r1bQkb1r/ppp2ppp/2p5/4Pn2/8/5N2/PPP2PPP/RNB2RK1 b kq - -1 8",
        ]
        assert len(correct_fens) == len(invalid_syntax_fens)
        for correct_fen, invalid_syntax_fen in zip(correct_fens, invalid_syntax_fens):
            old_del_counter = Stockfish._del_counter
            if correct_fen is not None:
                assert stockfish.is_fen_valid(correct_fen)
                assert stockfish._is_fen_syntax_valid(correct_fen)
            assert not stockfish.is_fen_valid(invalid_syntax_fen)
            assert not stockfish._is_fen_syntax_valid(invalid_syntax_fen)
            assert Stockfish._del_counter == old_del_counter + (
                2 if correct_fen is not None else 0
            )

        time.sleep(2.0)
        assert stockfish._stockfish.poll() is None
        assert stockfish.get_engine_parameters() == old_params
        assert stockfish.info == old_info
        assert stockfish._depth == old_depth
        assert stockfish.get_fen_position() == old_fen

    def test_send_quit_command(self, stockfish: Stockfish):
        assert stockfish._stockfish.poll() is None
        old_del_counter = Stockfish._del_counter
        stockfish.send_quit_command()
        assert stockfish._stockfish.poll() is not None
        stockfish.__del__()
        assert stockfish._stockfish.poll() is not None
        assert Stockfish._del_counter == old_del_counter + 1

    def test_set_option(self, stockfish: Stockfish):
        stockfish._set_option("MultiPV", 3)
        assert stockfish.get_engine_parameters()["MultiPV"] == 3
        stockfish._set_option("MultiPV", 6, False)  # update_parameters_attribute
        assert stockfish.get_engine_parameters()["MultiPV"] == 3

    def test_pick(self, stockfish: Stockfish):
        info = "info depth 10 seldepth 15 multipv 1 score cp -677 wdl 0 0 1000"
        line = info.split(" ")
        assert stockfish._pick(line, "depth") == "10"
        assert stockfish._pick(line, "multipv") == "1"
        assert stockfish._pick(line, "wdl", 3) == "1000"

    def test_convert_human_notation_to_sf_notation(self, stockfish: Stockfish):
        stockfish.set_fen_position(
            "rnbbk1nr/pPP1pp1p/1p2B3/2PpPN1Q/3p1B2/1N2Pq2/P4PPP/R3K2R w KQkq d6 0 2"
        )
        input_test_moves_1 = "exd6 Bxc8 cxd8Q+ cxd8R bxc8=Q bxc8Q bxa8=N cxd6".split()
        expected_outputs_1 = "e5d6 e6c8 c7d8Q  c7d8R b7c8Q  b7c8Q b7a8N  c5d6".split()

        for i in range(len(input_test_moves_1)):
            assert (
                stockfish.convert_human_notation_to_sf_notation(input_test_moves_1[i])
                == expected_outputs_1[i]
            )

        input_test_moves_2 = "gxf3 g2xf3 Bxf7+ Bxf7 nd6+ Nxe7 0-0  00  ".split()
        expected_outputs_2 = "g2f3 g2f3  e6f7  e6f7 f5d6 f5e7 e1g1 e1g1".split()

        for i in range(len(input_test_moves_2)):
            assert (
                stockfish.convert_human_notation_to_sf_notation(input_test_moves_2[i])
                == expected_outputs_2[i]
            )

        input_test_moves_3 = "Qxf7 Qxf7# e1g1 h1f1 O-O  nbxd4 Nfxd4 b3xd4 b3d4".split()
        expected_outputs_3 = "h5f7 h5f7  e1g1 h1f1 e1g1 b3d4  f5d4  b3d4  b3d4".split()

        for i in range(len(input_test_moves_3)):
            assert (
                stockfish.convert_human_notation_to_sf_notation(input_test_moves_3[i])
                == expected_outputs_3[i]
            )

        input_test_moves_4 = "Nb3xd4 c5c6 c6".split()
        expected_outputs_4 = "b3d4   c5c6 c5c6".split()

        for i in range(len(input_test_moves_4)):
            assert (
                stockfish.convert_human_notation_to_sf_notation(input_test_moves_4[i])
                == expected_outputs_4[i]
            )

        wrong_test_moves = "ed bxc8 bxa8 0-0-0 OOO Bd5 Nxg3 nbd4".split()

        for move in wrong_test_moves:
            with pytest.raises(ValueError):
                stockfish.convert_human_notation_to_sf_notation(move)

    @pytest.mark.parametrize(
        "fen",
        [
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b - - 10 20",
        ],
    )
    def test_get_num_pieces(self, stockfish: Stockfish, fen):
        stockfish.set_fen_position(fen)
        assert stockfish.get_num_pieces() == 32
        assert stockfish.get_num_pieces(file_range=["h", "H"]) == 4
        assert (
            stockfish.get_num_pieces(
                file_range=["a", "a"],
                pieces_to_count=[Stockfish.Piece.WHITE_PAWN, "r", "P"],
            )
            == 2
        )
        assert stockfish.get_num_pieces(rank_range=[2, 2]) == 8
        assert stockfish.get_num_pieces(rank_range=[2, 2], pieces_to_count=["p"]) == 0
        assert (
            stockfish.get_num_pieces(
                rank_range=[2, 2], pieces_to_count=[Stockfish.Piece.BLACK_PAWN]
            )
            == 0
        )
        assert stockfish.get_num_pieces(rank_range=[-1, -1], pieces_to_count=[]) == 0

        expected_num_pieces_per_rank = [8, 8, 0, 0, 0, 0, 8, 8]
        expected_num_pawns_per_rank = [0, 8, 0, 0, 0, 0, 8, 0]

        expected_num_white_pawns_per_rank = [0, 0, 0, 0, 0, 0, 8, 0]
        expected_num_black_pawns_per_rank = [0, 8, 0, 0, 0, 0, 0, 0]

        back_rank_pieces = ["R", "N", "B", "Q", "K", "B", "N", "R"]

        for i in range(8):
            a_file_plus_i = [chr(ord("a") + i), chr(ord("a") + i)]
            a_file_plus_7_minus_i = [chr(ord("a") + 7 - i), chr(ord("a") + 7 - i)]
            assert (
                stockfish.get_num_pieces(rank_range=[8 - i, 8 - i])
                == expected_num_pieces_per_rank[i]
            )
            assert (
                stockfish.get_num_pieces(
                    rank_range=[8 - i, 8 - i], file_range=a_file_plus_i
                )
                == expected_num_pieces_per_rank[i] / 8
            )

            assert (
                stockfish.get_num_pieces(
                    rank_range=[8 - i, 8 - i],
                    pieces_to_count=[
                        Stockfish.Piece.WHITE_PAWN,
                        Stockfish.Piece.BLACK_PAWN,
                    ],
                )
                == expected_num_pawns_per_rank[i]
            )
            assert (
                stockfish.get_num_pieces(
                    rank_range=[8 - i, 8 - i],
                    pieces_to_count=["P", "p"],
                    file_range=a_file_plus_7_minus_i,
                )
                == expected_num_pawns_per_rank[i] / 8
            )

            assert (
                stockfish.get_num_pieces(
                    rank_range=[8 - i, 8 - i],
                    pieces_to_count=[Stockfish.Piece.WHITE_PAWN],
                )
                == expected_num_white_pawns_per_rank[i]
            )
            assert (
                stockfish.get_num_pieces(
                    rank_range=[8 - i, 8 - i],
                    pieces_to_count=["P"],
                    file_range=a_file_plus_i,
                )
                == expected_num_white_pawns_per_rank[i] / 8
            )

            assert (
                stockfish.get_num_pieces(
                    rank_range=[8 - i, 8 - i], pieces_to_count=["p"]
                )
                == expected_num_black_pawns_per_rank[i]
            )
            assert (
                stockfish.get_num_pieces(
                    rank_range=[8 - i, 8 - i],
                    pieces_to_count=[Stockfish.Piece.BLACK_PAWN],
                    file_range=a_file_plus_7_minus_i,
                )
                == expected_num_black_pawns_per_rank[i] / 8
            )

            assert stockfish.get_num_pieces(file_range=a_file_plus_i) == 4
            assert stockfish.get_num_pieces(
                file_range=a_file_plus_i, rank_range=[8 - i, 8 - i]
            ) == (0 if 3 <= 8 - i <= 6 else 1)

            assert (
                stockfish.get_num_pieces(
                    file_range=a_file_plus_i,
                    pieces_to_count=[Stockfish.Piece.WHITE_PAWN, "p"],
                )
                == 2
            )
            assert stockfish.get_num_pieces(
                file_range=a_file_plus_i,
                rank_range=[i + 1, i + 1],
                pieces_to_count=["P"],
            ) == (1 if i + 1 == 2 else 0)
            assert stockfish.get_num_pieces(
                file_range=a_file_plus_i,
                rank_range=[8 - i, 8 - i],
                pieces_to_count=[Stockfish.Piece.BLACK_PAWN],
            ) == (1 if 8 - i == 7 else 0)

            for j in range(len(back_rank_pieces)):
                i_j_in_sync = (i == j) or (i == 7 - j and i not in [3, 4])
                assert stockfish.get_num_pieces(
                    file_range=a_file_plus_i,
                    pieces_to_count=[back_rank_pieces[j], back_rank_pieces[j].lower()],
                ) == (2 if i_j_in_sync else 0)
                assert stockfish.get_num_pieces(
                    file_range=a_file_plus_i, pieces_to_count=[back_rank_pieces[j]]
                ) == (1 if i_j_in_sync else 0)
                assert stockfish.get_num_pieces(
                    file_range=a_file_plus_i,
                    pieces_to_count=[back_rank_pieces[j].lower()],
                ) == (1 if i_j_in_sync else 0)

        with pytest.raises(ValueError):
            stockfish.get_num_pieces(rank_range=[-1, -1])
        with pytest.raises(ValueError):
            stockfish.get_num_pieces(rank_range=[2, 9])
        with pytest.raises(ValueError):
            stockfish.get_num_pieces(rank_range=[9, 2])
        with pytest.raises(ValueError):
            stockfish.get_num_pieces(file_range=["ah"])
        with pytest.raises(ValueError):
            stockfish.get_num_pieces(file_range=["a", "j"])
        with pytest.raises(ValueError):
            stockfish.get_num_pieces(pieces_to_count=["K", "q", "L"])
        with pytest.raises(ValueError):
            stockfish.get_num_pieces(pieces_to_count=["K", 3, "r"])
        with pytest.raises(ValueError):
            stockfish.get_num_pieces(
                pieces_to_count=["K", Stockfish.Piece.BLACK_QUEEN, "L"]
            )

    def test_get_num_pieces_custom_ranges(self, stockfish: Stockfish):
        stockfish.set_fen_position(
            "r4rk1/pp1bbpp1/1qp2n2/3p4/3PnN1p/1PNQ2P1/PB2PPBP/2R1R1K1 w q - 0 1"
        )
        assert stockfish.get_num_pieces() == 30
        assert stockfish.get_num_pieces(file_range=["a", "d"]) == 14
        assert stockfish.get_num_pieces(file_range=["a", "d"], rank_range=[1, 4]) == 7
        assert (
            stockfish.get_num_pieces(file_range=["f", "h"], pieces_to_count=["P", "p"])
            == 6
        )
        assert (
            stockfish.get_num_pieces(rank_range=[4, 6], pieces_to_count=["P", "p"]) == 4
        )
        assert stockfish.get_num_pieces(rank_range=[7, 8], file_range=["e", "H"]) == 5

    def test_get_engine_parameters(self, stockfish: Stockfish):
        params = stockfish.get_engine_parameters()
        params.update({"Skill Level": 10})
        assert params["Skill Level"] == 10
        assert stockfish._parameters["Skill Level"] == 20
