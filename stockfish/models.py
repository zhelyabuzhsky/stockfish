"""
    This module implements the Stockfish class.

    :copyright: (c) 2016-2021 by Ilya Zhelyabuzhsky.
    :license: MIT, see LICENSE for more details.
"""

import subprocess
from typing import Any, List, Optional
import copy
from os import path
from dataclasses import dataclass
from enum import Enum


class Stockfish:
    """Integrates the Stockfish chess engine with Python."""

    def __init__(
        self, path: str = "stockfish", depth: int = 15, parameters: dict = None
    ) -> None:
        self._DEFAULT_STOCKFISH_PARAMS = {
            "Debug Log File": "",
            "Contempt": 0,
            "Min Split Depth": 0,
            "Threads": 1,
            "Ponder": "false",
            "Hash": 1024,
            "MultiPV": 1,
            "Skill Level": 20,
            "Move Overhead": 10,
            "Minimum Thinking Time": 20,
            "Slow Mover": 100,
            "UCI_Chess960": "false",
            "UCI_LimitStrength": "false",
            "UCI_Elo": 1350,
        }
        self._stockfish = subprocess.Popen(
            path,
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        self._has_quit_command_been_sent = False

        self._stockfish_major_version: int = int(
            self._read_line().split(" ")[1].split(".")[0]
        )

        self._put("uci")

        self.depth = str(depth)
        self.info: str = ""

        self._parameters: dict = {}
        self.update_engine_parameters(self._DEFAULT_STOCKFISH_PARAMS)
        self.update_engine_parameters(parameters)

        if self.does_current_engine_version_have_wdl_option():
            self._set_option("UCI_ShowWDL", "true", False)

        self._prepare_for_new_position(True)

    def get_parameters(self) -> dict:
        """Returns current board position.

        Returns:
            Dictionary of current Stockfish engine's parameters.
        """
        return self._parameters

    def update_engine_parameters(self, new_param_valuesP: Optional[dict]) -> None:
        """Updates the stockfish parameters.

        Args:
            new_param_values:
                Contains (key, value) pairs which will be used to update
                the _parameters dictionary.

        Returns:
            None
        """
        if not new_param_valuesP:
            return

        new_param_values = copy.deepcopy(new_param_valuesP)

        if len(self._parameters) > 0:
            for key in new_param_values:
                if key not in self._parameters:
                    raise ValueError(f"'{key}' is not a key that exists.")

        if ("Skill Level" in new_param_values) != (
            "UCI_Elo" in new_param_values
        ) and "UCI_LimitStrength" not in new_param_values:
            # This means the user wants to update the Skill Level or UCI_Elo (only one,
            # not both), and that they didn't specify a new value for UCI_LimitStrength.
            # So, update UCI_LimitStrength, in case it's not the right value currently.
            if "Skill Level" in new_param_values:
                new_param_values.update({"UCI_LimitStrength": "false"})
            elif "UCI_Elo" in new_param_values:
                new_param_values.update({"UCI_LimitStrength": "true"})

        if "Threads" in new_param_values:
            # Recommended to set the hash param after threads.
            threads_value = new_param_values["Threads"]
            del new_param_values["Threads"]
            hash_value = None
            if "Hash" in new_param_values:
                hash_value = new_param_values["Hash"]
                del new_param_values["Hash"]
            else:
                hash_value = self._parameters["Hash"]
            new_param_values["Threads"] = threads_value
            new_param_values["Hash"] = hash_value

        for name, value in new_param_values.items():
            self._set_option(name, value, True)
        self.set_fen_position(self.get_fen_position(), False)
        # Getting SF to set the position again, since UCI option(s) have been updated.

    def reset_engine_parameters(self) -> None:
        """Resets the stockfish parameters.

        Returns:
            None
        """
        self.update_engine_parameters(self._DEFAULT_STOCKFISH_PARAMS)

    def _prepare_for_new_position(self, send_ucinewgame_token: bool = True) -> None:
        if send_ucinewgame_token:
            self._put("ucinewgame")
        self._is_ready()
        self.info = ""

    def _put(self, command: str) -> None:
        if not self._stockfish.stdin:
            raise BrokenPipeError()
        if self._stockfish.poll() is None and not self._has_quit_command_been_sent:
            self._stockfish.stdin.write(f"{command}\n")
            self._stockfish.stdin.flush()
            if command == "quit":
                self._has_quit_command_been_sent = True

    def _read_line(self) -> str:
        if not self._stockfish.stdout:
            raise BrokenPipeError()
        return self._stockfish.stdout.readline().strip()

    def _set_option(
        self, name: str, value: Any, update_parameters_attribute: bool = True
    ) -> None:
        self._put(f"setoption name {name} value {value}")
        if update_parameters_attribute:
            self._parameters.update({name: value})
        self._is_ready()

    def _is_ready(self) -> None:
        self._put("isready")
        while True:
            if self._read_line() == "readyok":
                return

    def _go(self) -> None:
        self._put(f"go depth {self.depth}")

    def _go_time(self, time: int) -> None:
        self._put(f"go movetime {time}")

    def _go_remaining_time(self, wtime: Optional[int], btime: Optional[int]) -> None:
        cmd = "go"
        if wtime is not None:
            cmd += f" wtime {wtime}"
        if btime is not None:
            cmd += f" btime {btime}"
        self._put(cmd)

    @staticmethod
    def _convert_move_list_to_str(moves: List[str]) -> str:
        result = ""
        for move in moves:
            result += f"{move} "
        return result.strip()

    def set_position(self, moves: List[str] = None) -> None:
        """Sets current board position.

        Args:
            moves:
              A list of moves to set this position on the board.
              Must be in full algebraic notation.
              example: ['e2e4', 'e7e5']
        """
        self._prepare_for_new_position(True)
        if moves is None:
            moves = []
        self._put(f"position startpos moves {self._convert_move_list_to_str(moves)}")

    def make_moves_from_current_position(self, moves: List[str]) -> None:
        """Sets a new position by playing the moves from the current position.

        Args:
            moves:
              A list of moves to play in the current position, in order to reach a new position.
              Must be in full algebraic notation.
              Example: ["g4d7", "a8b8", "f1d1"]
        """
        if moves == []:
            raise ValueError(
                "No moves sent in to the make_moves_from_current_position function."
            )
        self._prepare_for_new_position(False)
        self._put(
            f"position fen {self.get_fen_position()} moves {self._convert_move_list_to_str(moves)}"
        )

    def get_board_visual(self) -> str:
        """Returns a visual representation of the current board position.

        Returns:
            String of visual representation of the chessboard with its pieces in current position.
        """
        self._put("d")
        board_rep = ""
        count_lines = 0
        while count_lines < 17:
            board_str = self._read_line()
            if "+" in board_str or "|" in board_str:
                count_lines += 1
                board_rep += f"{board_str}\n"
        if self._stockfish_major_version >= 12:
            board_str = self._read_line()
            board_rep += f"  {board_str}\n"
        return board_rep

    def get_fen_position(self) -> str:
        """Returns current board position in Forsyth–Edwards notation (FEN).

        Returns:
            String with current position in Forsyth–Edwards notation (FEN)
        """
        self._put("d")
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            if splitted_text[0] == "Fen:":
                return " ".join(splitted_text[1:])

    def set_skill_level(self, skill_level: int = 20) -> None:
        """Sets current skill level of stockfish engine.

        Args:
            skill_level:
              Skill Level option between 0 (weakest level) and 20 (full strength)

        Returns:
            None
        """
        self.update_engine_parameters(
            {"UCI_LimitStrength": "false", "Skill Level": skill_level}
        )

    def set_elo_rating(self, elo_rating: int = 1350) -> None:
        """Sets current elo rating of stockfish engine, ignoring skill level.

        Args:
            elo_rating: Aim for an engine strength of the given Elo

        Returns:
            None
        """
        self.update_engine_parameters(
            {"UCI_LimitStrength": "true", "UCI_Elo": elo_rating}
        )

    def set_fen_position(
        self, fen_position: str, send_ucinewgame_token: bool = True
    ) -> None:
        """Sets current board position in Forsyth–Edwards notation (FEN).

        Args:
            fen_position:
              FEN string of board position.

            send_ucinewgame_token:
              Whether to send the "ucinewgame" token to the Stockfish engine.
              The most prominent effect this will have is clearing Stockfish's transposition table,
              which should be done if the new position is unrelated to the current position.

        Returns:
            None
        """
        self._prepare_for_new_position(send_ucinewgame_token)
        self._put(f"position fen {fen_position}")

    def get_best_move(self, wtime: int = None, btime: int = None) -> Optional[str]:
        """Returns best move with current position on the board.
        wtime and btime arguments influence the search only if provided.

        Returns:
            A string of move in algebraic notation or None, if it's a mate now.
        """
        if wtime is not None or btime is not None:
            self._go_remaining_time(wtime, btime)
        else:
            self._go()
        last_text: str = ""
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            if splitted_text[0] == "bestmove":
                if splitted_text[1] == "(none)":
                    return None
                self.info = last_text
                return splitted_text[1]
            last_text = text

    def get_best_move_time(self, time: int = 1000) -> Optional[str]:
        """Returns best move with current position on the board after a determined time

        Args:
            time:
              Time for stockfish to determine best move in milliseconds (int)

        Returns:
            A string of move in algebraic notation or None, if it's a mate now.
        """
        self._go_time(time)
        last_text: str = ""
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            if splitted_text[0] == "bestmove":
                if splitted_text[1] == "(none)":
                    return None
                self.info = last_text
                return splitted_text[1]
            last_text = text

    def is_move_correct(self, move_value: str) -> bool:
        """Checks new move.

        Args:
            move_value:
              New move value in algebraic notation.

        Returns:
            True, if new move is correct, else False.
        """
        self._put(f"go depth 1 searchmoves {move_value}")
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            if splitted_text[0] == "bestmove":
                return splitted_text[1] != "(none)"

    def get_wdl_stats(self) -> Optional[List]:
        """Returns Stockfish's win/draw/loss stats for the side to move.

        Returns:
            A list of three integers, unless the game is over (in which case,
            None is returned).
        """

        if not self.does_current_engine_version_have_wdl_option():
            raise RuntimeError(
                "Your version of Stockfish isn't recent enough to have the UCI_ShowWDL option."
            )
        self._go()
        lines = []
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            lines.append(splitted_text)
            if splitted_text[0] == "bestmove":
                break
        for current_line in reversed(lines):
            if current_line[0] == "bestmove" and current_line[1] == "(none)":
                return None
            elif "multipv" in current_line:
                index_of_multipv = current_line.index("multipv")
                if current_line[index_of_multipv + 1] == "1" and "wdl" in current_line:
                    index_of_wdl = current_line.index("wdl")
                    wdl_stats = []
                    for i in range(1, 4):
                        wdl_stats.append(int(current_line[index_of_wdl + i]))
                    return wdl_stats
        raise RuntimeError("Reached the end of the get_wdl_stats function.")

    def does_current_engine_version_have_wdl_option(self) -> bool:
        """Returns whether the user's version of Stockfish has the option
           to display WDL stats.

        Returns:
            True, if SF has the option -- False otherwise.
        """

        self._put("uci")
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            if splitted_text[0] == "uciok":
                return False
            elif "UCI_ShowWDL" in splitted_text:
                return True

    def get_evaluation(self) -> dict:
        """Evaluates current position

        Returns:
            A dictionary of the current advantage with "type" as "cp" (centipawns) or "mate" (checkmate in)
        """

        evaluation = dict()
        fen_position = self.get_fen_position()
        if "w" in fen_position:  # w can only be in FEN if it is whites move
            compare = 1
        else:  # stockfish shows advantage relative to current player, convention is to do white positive
            compare = -1
        self._put(f"position {fen_position}")
        self._go()
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            if splitted_text[0] == "info":
                for n in range(len(splitted_text)):
                    if splitted_text[n] == "score":
                        evaluation = {
                            "type": splitted_text[n + 1],
                            "value": int(splitted_text[n + 2]) * compare,
                        }
            elif splitted_text[0] == "bestmove":
                return evaluation

    def get_top_moves(self, num_top_moves: int = 5) -> List[dict]:
        """Returns info on the top moves in the position.

        Args:
            num_top_moves:
                The number of moves to return info on, assuming there are at least
                those many legal moves.

        Returns:
            A list of dictionaries. In each dictionary, there are keys for Move, Centipawn, and Mate;
            the corresponding value for either the Centipawn or Mate key will be None.
            If there are no moves in the position, an empty list is returned.
        """

        if num_top_moves <= 0:
            raise ValueError("num_top_moves is not a positive number.")
        old_MultiPV_value = self._parameters["MultiPV"]
        if num_top_moves != self._parameters["MultiPV"]:
            self._set_option("MultiPV", num_top_moves)
            self._parameters.update({"MultiPV": num_top_moves})
        self._go()
        lines = []
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            lines.append(splitted_text)
            if splitted_text[0] == "bestmove":
                break
        top_moves: List[dict] = []
        multiplier = 1 if ("w" in self.get_fen_position()) else -1
        for current_line in reversed(lines):
            if current_line[0] == "bestmove":
                if current_line[1] == "(none)":
                    top_moves = []
                    break
            elif (
                ("multipv" in current_line)
                and ("depth" in current_line)
                and current_line[current_line.index("depth") + 1] == self.depth
            ):
                multiPV_number = int(current_line[current_line.index("multipv") + 1])
                if multiPV_number <= num_top_moves:
                    has_centipawn_value = "cp" in current_line
                    has_mate_value = "mate" in current_line
                    if has_centipawn_value == has_mate_value:
                        raise RuntimeError(
                            "Having a centipawn value and mate value should be mutually exclusive."
                        )
                    top_moves.insert(
                        0,
                        {
                            "Move": current_line[current_line.index("pv") + 1],
                            "Centipawn": int(current_line[current_line.index("cp") + 1])
                            * multiplier
                            if has_centipawn_value
                            else None,
                            "Mate": int(current_line[current_line.index("mate") + 1])
                            * multiplier
                            if has_mate_value
                            else None,
                        },
                    )
            else:
                break
        if old_MultiPV_value != self._parameters["MultiPV"]:
            self._set_option("MultiPV", old_MultiPV_value)
            self._parameters.update({"MultiPV": old_MultiPV_value})
        return top_moves

    @dataclass
    class BenchmarkParameters:
        ttSize: int = 16
        threads: int = 1
        limit: int = 13
        fenFile: str = "default"
        limitType: str = "depth"
        evalType: str = "mixed"

        def __post_init__(self):
            self.ttSize = self.ttSize if self.ttSize in range(1, 128001) else 16
            self.threads = self.threads if self.threads in range(1, 513) else 1
            self.limit = self.limit if self.limit in range(1, 10001) else 13
            self.fenFile = (
                self.fenFile
                if self.fenFile.endswith(".fen") and path.isfile(self.fenFile)
                else "default"
            )
            self.limitType = (
                self.limitType
                if self.limitType in ["depth", "perft", "nodes", "movetime"]
                else "depth"
            )
            self.evalType = (
                self.evalType
                if self.evalType in ["mixed", "classical", "NNUE"]
                else "mixed"
            )

    def benchmark(self, params: BenchmarkParameters) -> str:
        """Benchmark will run the bench command with BenchmarkParameters.
        It is an Additional custom non-UCI command, mainly for debugging.
        Do not use this command during a search!
        """
        if type(params) != self.BenchmarkParameters:
            params = self.BenchmarkParameters()

        self._put(
            f"bench {params.ttSize} {params.threads} {params.limit} {params.fenFile} {params.limitType} {params.evalType}"
        )
        last_text: str = ""
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            if splitted_text[0] == "Nodes/second":
                last_text = text
                return last_text
            last_text = text

    def set_depth(self, depth_value: int = 2) -> None:
        """Sets current depth of stockfish engine.

        Args:
            depth_value: Depth option higher than 1
        """
        self.depth = str(depth_value)

    class Piece(Enum):
        WHITE_PAWN = "P"
        BLACK_PAWN = "p"
        WHITE_KNIGHT = "N"
        BLACK_KNIGHT = "n"
        WHITE_BISHOP = "B"
        BLACK_BISHOP = "b"
        WHITE_ROOK = "R"
        BLACK_ROOK = "r"
        WHITE_QUEEN = "Q"
        BLACK_QUEEN = "q"
        WHITE_KING = "K"
        BLACK_KING = "k"

    def get_what_is_on_square(self, square: str) -> Optional[Piece]:
        """Returns what is on the specified square.

        Args:
            square:
                The coordinate of the square in question. E.g., e4.

        Returns:
            Either one of the 12 enum members in the Piece enum, or the None
            object if the square is empty.
        """

        file_letter = square[0].lower()
        rank_num = int(square[1])
        if (
            len(square) != 2
            or file_letter < "a"
            or file_letter > "h"
            or square[1] < "1"
            or square[1] > "8"
        ):
            raise ValueError(
                "square argument to the get_what_is_on_square function isn't valid."
            )
        rank_visual = self.get_board_visual().splitlines()[17 - 2 * rank_num]
        piece_as_char = rank_visual[2 + (ord(file_letter) - ord("a")) * 4]
        if piece_as_char == " ":
            return None
        else:
            return Stockfish.Piece(piece_as_char)

    class Capture(Enum):
        DIRECT_CAPTURE = "direct capture"
        EN_PASSANT = "en passant"
        NO_CAPTURE = "no capture"

    def will_move_be_a_capture(self, move_value: str) -> Capture:
        """Returns whether the proposed move will be a direct capture,
           en passant, or not a capture at all.

        Args:
            move_value:
                The proposed move, in the notation that Stockfish uses.
                E.g., "e2e4", "g1f3", etc.

        Returns one of the following members of the Capture enum:
            DIRECT_CAPTURE if the move will be a direct capture.
            EN_PASSANT if the move is a capture done with en passant.
            NO_CAPTURE if the move does not capture anything.
        """
        if not self.is_move_correct(move_value):
            raise ValueError("The proposed move is not valid in the current position.")
        starting_square_piece = self.get_what_is_on_square(move_value[:2])
        ending_square_piece = self.get_what_is_on_square(move_value[-2:])
        if ending_square_piece != None:
            if self._parameters["UCI_Chess960"] == "false":
                return Stockfish.Capture.DIRECT_CAPTURE
            else:
                # Check for Chess960 castling:
                castling_pieces = [
                    [Stockfish.Piece.WHITE_KING, Stockfish.Piece.WHITE_ROOK],
                    [Stockfish.Piece.BLACK_KING, Stockfish.Piece.BLACK_ROOK],
                ]
                if [starting_square_piece, ending_square_piece] in castling_pieces:
                    return Stockfish.Capture.NO_CAPTURE
                else:
                    return Stockfish.Capture.DIRECT_CAPTURE
        elif move_value[-2:] == self.get_fen_position().split()[
            3
        ] and starting_square_piece in [
            Stockfish.Piece.WHITE_PAWN,
            Stockfish.Piece.BLACK_PAWN,
        ]:
            return Stockfish.Capture.EN_PASSANT
        else:
            return Stockfish.Capture.NO_CAPTURE

    def get_stockfish_major_version(self):
        """Returns Stockfish engine major version.

        Returns:
            Current stockfish major version
        """

        return self._stockfish_major_version

    def is_development_build_of_engine(self) -> bool:
        """Returns whether the version of Stockfish being used is a
           development build.

        Returns:
            True if the major version is a date, indicating SF is a
            development build. E.g., 020122 is the major version of the SF
            development build released on Jan 2, 2022. Otherwise, False is
            returned (which means the engine is an official release of SF).
        """
        return (
            self._stockfish_major_version >= 10109
            and self._stockfish_major_version <= 311299
        )

    def __del__(self) -> None:
        if self._stockfish.poll() is None:
            self._put("quit")
            self._stockfish.kill()
            while self._stockfish.poll() is None:
                pass
