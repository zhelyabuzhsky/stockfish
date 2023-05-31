"""
    This module implements the Stockfish class.

    :copyright: (c) 2016-2021 by Ilya Zhelyabuzhsky.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import annotations
import subprocess
from typing import Any, List, Optional, Union
import copy
from os import path
from dataclasses import dataclass
from enum import Enum
import re
import warnings


class Stockfish:
    """Integrates the [Stockfish chess engine](https://stockfishchess.org/) with Python."""

    _del_counter = 0
    # Used in test_models: will count how many times the del function is called.

    def __init__(
        self,
        path: str = "stockfish",
        depth: int = 15,
        parameters: Optional[dict] = None,
        num_nodes: int = 1000000,
        turn_perspective: bool = True,
        debug_view: bool = False,
    ) -> None:
        """Initializes the Stockfish engine.

        Example:
            >>> from stockfish import Stockfish
            >>> stockfish = Stockfish()
        """
        self._DEFAULT_STOCKFISH_PARAMS = {
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
        self._debug_view: bool = debug_view

        self._path: str = path
        self._stockfish = subprocess.Popen(
            self._path,
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        self._has_quit_command_been_sent: bool = False

        self._stockfish_major_version: int = int(
            self._read_line().split(" ")[1].split(".")[0].replace("-", "")
        )

        self._put("uci")

        self.set_depth(depth)
        self.set_num_nodes(num_nodes)
        self.set_turn_perspective(turn_perspective)

        self.info: str = ""

        self._parameters: dict = {}
        self.update_engine_parameters(self._DEFAULT_STOCKFISH_PARAMS)
        self.update_engine_parameters(parameters)

        if self.does_current_engine_version_have_wdl_option():
            self._set_option("UCI_ShowWDL", True, False)

        self._prepare_for_new_position(True)

    def set_debug_view(self, activate: bool) -> None:
        self._debug_view = activate

    def get_engine_parameters(self) -> dict:
        """Returns the current engine parameters being used.

        Returns:
            Dictionary of current Stockfish engine's parameters.
        """
        return self._parameters

    def get_parameters(self) -> dict:
        """Returns the current engine parameters being used. *Deprecated, see `get_engine_parameters()`*."""

        raise ValueError(
            """The values for 'Ponder', 'UCI_Chess960', and 'UCI_LimitStrength' have been updated from
               strings to bools in a new release of the python stockfish package. As a result, this
               'get_parameters()' function has been deprecated, in an effort to avoid existing users
               unknowingly getting bugs. It has been replaced with 'get_engine_parameters()'."""
        )

    def update_engine_parameters(self, parameters: Optional[dict]) -> None:
        """Updates the Stockfish engine parameters.

        Args:
            parameters:
                Contains (key, value) pairs which will be used to update
                the current Stockfish engine's parameters.

        Returns:
            `None`

        Example:
            >>> stockfish.update_engine_parameters({'Threads': 2})
        """
        if not parameters:
            return

        new_param_values = copy.deepcopy(parameters)

        if len(self._parameters) > 0:
            for key in new_param_values:
                if key not in self._parameters:
                    raise ValueError(f"'{key}' is not a key that exists.")

                elif key in (
                    "Ponder",
                    "UCI_Chess960",
                    "UCI_LimitStrength",
                ) and not isinstance(new_param_values[key], bool):
                    raise ValueError(
                        f"The value for the '{key}' key has been updated from a string to a bool in a new release of the python stockfish package."
                    )

        if ("Skill Level" in new_param_values) != (
            "UCI_Elo" in new_param_values
        ) and "UCI_LimitStrength" not in new_param_values:
            # This means the user wants to update the Skill Level or UCI_Elo (only one,
            # not both), and that they didn't specify a new value for UCI_LimitStrength.
            # So, update UCI_LimitStrength, in case it's not the right value currently.
            if "Skill Level" in new_param_values:
                new_param_values.update({"UCI_LimitStrength": False})
            elif "UCI_Elo" in new_param_values:
                new_param_values.update({"UCI_LimitStrength": True})

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
            self._set_option(name, value)
        self.set_fen_position(self.get_fen_position(), False)
        # Getting SF to set the position again, since UCI option(s) have been updated.

    def reset_engine_parameters(self) -> None:
        """Resets the Stockfish engine parameters.

        Returns:
            `None`
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
            if self._debug_view:
                print(f">>> {command}\n")
            self._stockfish.stdin.write(f"{command}\n")
            self._stockfish.stdin.flush()
            if command == "quit":
                self._has_quit_command_been_sent = True

    def _read_line(self) -> str:
        if not self._stockfish.stdout:
            raise BrokenPipeError()
        if self._stockfish.poll() is not None:
            raise StockfishException("The Stockfish process has crashed")
        line = self._stockfish.stdout.readline().strip()
        if self._debug_view:
            print(line)
        return line

    def _set_option(
        self, name: str, value: Any, update_parameters_attribute: bool = True
    ) -> None:
        str_rep_value = str(value)
        if isinstance(value, bool):
            str_rep_value = str_rep_value.lower()
        self._put(f"setoption name {name} value {str_rep_value}")
        if update_parameters_attribute:
            self._parameters.update({name: value})
        self._is_ready()

    def _is_ready(self) -> None:
        self._put("isready")
        while self._read_line() != "readyok":
            pass

    def _go(self) -> None:
        self._put(f"go depth {self._depth}")

    def _go_nodes(self) -> None:
        self._put(f"go nodes {self._num_nodes}")

    def _go_time(self, time: int) -> None:
        self._put(f"go movetime {time}")

    def _go_remaining_time(self, wtime: Optional[int], btime: Optional[int]) -> None:
        cmd = "go"
        if wtime is not None:
            cmd += f" wtime {wtime}"
        if btime is not None:
            cmd += f" btime {btime}"
        self._put(cmd)

    def _on_weaker_setting(self) -> bool:
        return (
            self._parameters["UCI_LimitStrength"]
            or self._parameters["Skill Level"] < 20
        )

    def _weaker_setting_warning(self, message: str) -> None:
        """Will issue a warning, referring to the function that calls this one."""
        warnings.warn(message, stacklevel=3)

    def set_fen_position(
        self, fen_position: str, send_ucinewgame_token: bool = True
    ) -> None:
        """Sets current board position in Forsyth-Edwards notation (FEN).

        Args:
            fen_position:
              FEN string of board position.

            send_ucinewgame_token:
              Whether to send the `ucinewgame` token to the Stockfish engine.
              The most prominent effect this will have is clearing Stockfish's transposition table,
              which should be done if the new position is unrelated to the current position.

        Returns:
            `None`

        Example:
            >>> stockfish.set_fen_position("1nb1k1n1/pppppppp/8/6r1/5bqK/6r1/8/8 w - - 2 2")
        """
        self._prepare_for_new_position(send_ucinewgame_token)
        self._put(f"position fen {fen_position}")

    def set_position(self, moves: Optional[List[str]] = None) -> None:
        """Sets current board position.

        Args:
            moves:
              A list of moves to set this position on the board.
              Must be in full algebraic notation.

        Returns:
            `None`

        Example:
            >>> stockfish.set_position(['e2e4', 'e7e5'])
        """
        self.set_fen_position(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", True
        )
        self.make_moves_from_current_position(moves)

    def make_moves_from_current_position(self, moves: Optional[List[str]]) -> None:
        """Sets a new position by playing the moves from the current position.

        Args:
            moves:
              A list of moves to play in the current position, in order to reach a new position.
              Must be in full algebraic notation.

        Returns:
            `None`

        Example:
            >>> stockfish.make_moves_from_current_position(["g4d7", "a8b8", "f1d1"])
        """
        if not moves:
            return
        self._prepare_for_new_position(False)
        for move in moves:
            if not self.is_move_correct(move):
                raise ValueError(f"Cannot make move: {move}")
            self._put(f"position fen {self.get_fen_position()} moves {move}")

    def get_board_visual(self, perspective_white: bool = True) -> str:
        """Returns a visual representation of the current board position.

        Args:
            perspective_white:
              A boolean that indicates whether the board should be displayed from the
              perspective of white. `True` indicates White's perspective.

        Returns:
            String of visual representation of the chessboard with its pieces in current position.

            For example:
            ```
            +---+---+---+---+---+---+---+---+
            | r | n | b | q | k | b | n | r | 8
            +---+---+---+---+---+---+---+---+
            | p | p | p | p | p | p | p | p | 7
            +---+---+---+---+---+---+---+---+
            |   |   |   |   |   |   |   |   | 6
            +---+---+---+---+---+---+---+---+
            |   |   |   |   |   |   |   |   | 5
            +---+---+---+---+---+---+---+---+
            |   |   |   |   |   |   |   |   | 4
            +---+---+---+---+---+---+---+---+
            |   |   |   |   |   |   |   |   | 3
            +---+---+---+---+---+---+---+---+
            | P | P | P | P | P | P | P | P | 2
            +---+---+---+---+---+---+---+---+
            | R | N | B | Q | K | B | N | R | 1
            +---+---+---+---+---+---+---+---+
              a   b   c   d   e   f   g   h
            ```
        """
        self._put("d")
        board_rep_lines: List[str] = []
        count_lines: int = 0
        while count_lines < 17:
            board_str: str = self._read_line()
            if "+" in board_str or "|" in board_str:
                count_lines += 1
                if perspective_white:
                    board_rep_lines.append(f"{board_str}")
                else:
                    # If the board is to be shown from black's point of view, all lines are
                    # inverted horizontally and at the end the order of the lines is reversed.
                    board_part = board_str[:33]
                    # To keep the displayed numbers on the right side,
                    # only the string representing the board is flipped.
                    number_part = board_str[33:] if len(board_str) > 33 else ""
                    board_rep_lines.append(f"{board_part[::-1]}{number_part}")
        if not perspective_white:
            board_rep_lines = board_rep_lines[::-1]
        board_str = self._read_line()
        if "a   b   c" in board_str:
            # Engine being used is recent enough to have coordinates, so add them:
            if perspective_white:
                board_rep_lines.append(f"  {board_str}")
            else:
                board_rep_lines.append(f"  {board_str[::-1]}")
        while "Checkers" not in self._read_line():
            # Gets rid of the remaining lines in _stockfish.stdout.
            # "Checkers" is in the last line outputted by Stockfish for the "d" command.
            pass
        board_rep = "\n".join(board_rep_lines) + "\n"
        return board_rep

    def get_fen_position(self) -> str:
        """Returns current board position in Forsyth-Edwards notation (FEN).

        Returns:
            String of current board position in Forsyth-Edwards notation (FEN).

            For example: `rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1`
        """
        self._put("d")
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            if splitted_text[0] == "Fen:":
                while "Checkers" not in self._read_line():
                    pass
                return " ".join(splitted_text[1:])

    def set_skill_level(self, skill_level: int = 20) -> None:
        """Sets current skill level of stockfish engine.

        Args:
            skill_level:
              Skill Level option between 0 (weakest level) and 20 (full strength)

        Returns:
            `None`

        Example:
            >>> stockfish.set_skill_level(10)
        """
        self.update_engine_parameters(
            {"UCI_LimitStrength": False, "Skill Level": skill_level}
        )

    def set_elo_rating(self, elo_rating: int = 1350) -> None:
        """Sets current Elo rating of Stockfish engine, ignoring skill level.

        Args:
            elo_rating: Aim for an engine strength of the given Elo

        Returns:
            `None`

        Example:
            >>> stockfish.set_elo_rating(2500)
        """
        self.update_engine_parameters(
            {"UCI_LimitStrength": True, "UCI_Elo": elo_rating}
        )

    def resume_full_strength(self) -> None:
        """Puts Stockfish back to full strength, if you've previously lowered the elo or skill level.

        Returns:
            `None`

        Example:
            >>> stockfish.reset_to_full_strength()
        """
        self.update_engine_parameters({"UCI_LimitStrength": False, "Skill Level": 20})

    def set_depth(self, depth: int = 15) -> None:
        """Sets current depth of Stockfish engine.

        Args:
            depth: Depth as integer 1 or higher

        Returns:
            `None`

        Example:
            >>> stockfish.set_depth(16)
        """
        if not isinstance(depth, int) or depth < 1 or isinstance(depth, bool):
            raise TypeError("depth must be an integer higher than 0")
        self._depth = depth

    def get_depth(self) -> int:
        """Returns configured depth to search

        Returns:
            `Integer`
        """
        return self._depth

    def set_num_nodes(self, num_nodes: int = 1000000) -> None:
        """Sets current number of nodes of Stockfish engine.

        Args:
            num_nodes: Number of nodes for Stockfish to search.

        Returns:
            `None`

        Example:
            >>> stockfish.set_num_nodes(1000000)
        """
        if (
            not isinstance(num_nodes, int)
            or isinstance(num_nodes, bool)
            or num_nodes < 1
        ):
            raise TypeError("num_nodes must be an integer higher than 0")
        self._num_nodes: int = num_nodes

    def get_num_nodes(self) -> int:
        """Returns configured number of nodes to search

        Returns:
            `Integer`
        """
        return self._num_nodes

    def set_turn_perspective(self, turn_perspective: bool = True) -> None:
        """Sets perspective of centipawn and WDL evaluations.

        Args:
            turn_perspective:
              Boolean whether perspective is turn-based. Default `True`.
              If `False`, returned evaluations are from White's perspective.

        Returns:
            `None`

        Example:
            >>> stockfish.set_turn_perspective(False)
        """
        if not isinstance(turn_perspective, bool):
            raise TypeError("turn_perspective must be a Boolean")
        self._turn_perspective = turn_perspective

    def get_turn_perspective(self) -> bool:
        """Returns whether centipawn and WDL values are set from turn perspective.
        Returns:
            `Boolean`
        """
        return self._turn_perspective

    def get_best_move(
        self, wtime: Optional[int] = None, btime: Optional[int] = None
    ) -> Optional[str]:
        """Returns best move with current position on the board.
        `wtime` and `btime` arguments influence the search only if provided.

        Args:
            wtime:
                Time for white player in milliseconds (int)
            btime:
                Time for black player in milliseconds (int)

        Returns:
            A string of move in algebraic notation, or `None` if it's a mate now.

        Example:
            >>> move = stockfish.get_best_move(wtime=1000, btime=1000)
        """
        if wtime is not None or btime is not None:
            self._go_remaining_time(wtime, btime)
        else:
            self._go()
        return self._get_best_move_from_sf_popen_process()

    def get_best_move_time(self, time: int = 1000) -> Optional[str]:
        """Returns best move with current position on the board after a determined time

        Args:
            time:
              Time for Stockfish to determine best move in milliseconds (int)

        Returns:
            A string of move in algebraic notation, or `None` if it's a mate now.

        Example:
            >>> move = stockfish.get_best_move_time(1000)
        """
        self._go_time(time)
        return self._get_best_move_from_sf_popen_process()

    def _get_best_move_from_sf_popen_process(self) -> Optional[str]:
        # Precondition - a "go" command must have been sent to SF before calling this function.
        # This function needs existing output to read from the SF popen process.
        last_text: str = ""
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            if splitted_text[0] == "bestmove":
                self.info = last_text
                return None if splitted_text[1] == "(none)" else splitted_text[1]
            last_text = text

    @staticmethod
    def _is_fen_syntax_valid(fen: str) -> bool:
        # Code for this function taken from: https://gist.github.com/Dani4kor/e1e8b439115878f8c6dcf127a4ed5d3e
        # Some small changes have been made to the code.
        regexMatch = re.match(
            r"\s*^(((?:[rnbqkpRNBQKP1-8]+\/){7})[rnbqkpRNBQKP1-8]+)\s([b|w])\s(-|[K|Q|k|q]{1,4})\s(-|[a-h][1-8])\s(\d+\s\d+)$",
            fen,
        )
        if not regexMatch:
            return False
        regexList = regexMatch.groups()
        if len(regexList[0].split("/")) != 8:
            return False  # 8 rows not present.
        for fenPart in regexList[0].split("/"):
            field_sum: int = 0
            previous_was_digit: bool = False
            for c in fenPart:
                if c in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    if previous_was_digit:
                        return False  # Two digits next to each other.
                    field_sum += int(c)
                    previous_was_digit = True
                elif c.lower() in ["p", "n", "b", "r", "q", "k"]:
                    field_sum += 1
                    previous_was_digit = False
                else:
                    return False  # Invalid character.
            if field_sum != 8:
                return False  # One of the rows doesn't have 8 columns.
        return True

    def is_fen_valid(self, fen: str) -> bool:
        """Checks if FEN string is valid.

        Returns:
            `Boolean`

        Example:
            >>> is_valid = stockfish.is_fen_valid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        """
        if not Stockfish._is_fen_syntax_valid(fen):
            return False
        temp_sf: Stockfish = Stockfish(path=self._path, parameters={"Hash": 1})
        # Using a new temporary SF instance, in case the fen is an illegal position that causes
        # the SF process to crash.
        best_move: Optional[str] = None
        temp_sf.set_fen_position(fen, False)
        try:
            temp_sf._put("go depth 10")
            best_move = temp_sf._get_best_move_from_sf_popen_process()
        except StockfishException:
            # If a StockfishException is thrown, then it happened in read_line() since the SF process crashed.
            # This is likely due to the position being illegal, so set the var to false:
            return False
        else:
            return best_move is not None
        finally:
            temp_sf.__del__()
            # Calling this function before returning from either the except or else block above.
            # The __del__ function should generally be called implicitly by python when this
            # temp_sf object goes out of scope, but calling it explicitly guarantees this will happen.

    def is_move_correct(self, move_value: str) -> bool:
        """Checks new move.

        Args:
            move_value:
              New move value in algebraic notation.

        Returns:
            `True` if new move is correct, otherwise `False`.

        Example:
            >>> is_correct = stockfish.is_move_correct("f4f5")
        """
        old_self_info = self.info
        self._put(f"go depth 1 searchmoves {move_value}")
        is_move_correct = self._get_best_move_from_sf_popen_process() is not None
        self.info = old_self_info
        return is_move_correct

    def get_wdl_stats(self) -> Optional[List[int]]:
        """Returns Stockfish's win/draw/loss stats for the side to move.

        Returns:
            A list of three integers, unless the game is over (in which case
            `None` is returned).
        """
        if not self.does_current_engine_version_have_wdl_option():
            raise RuntimeError(
                "Your version of Stockfish isn't recent enough to have the UCI_ShowWDL option."
            )
        if self._on_weaker_setting():
            self._weaker_setting_warning(
                """Note that even though you've set Stockfish to play on a weaker elo or skill level,"""
                + """ get_wdl_stats will still return full strength Stockfish's wdl stats of the position."""
            )

        self._go()
        lines: List[List[str]] = []
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
                    wdl_stats: List[int] = []
                    for i in range(1, 4):
                        wdl_stats.append(int(current_line[index_of_wdl + i]))
                    return wdl_stats
        raise RuntimeError("Reached the end of the get_wdl_stats function.")

    def does_current_engine_version_have_wdl_option(self) -> bool:
        """Returns whether the user's version of Stockfish has the option
           to display WDL stats.

        Returns:
            `True` if Stockfish has the `WDL` option, otherwise `False`.
        """
        self._put("uci")
        encountered_UCI_ShowWDL = False
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            if splitted_text[0] == "uciok":
                return encountered_UCI_ShowWDL
            elif "UCI_ShowWDL" in splitted_text:
                encountered_UCI_ShowWDL = True
                # Not returning right away, since the remaining lines should be read and
                # discarded. So continue the loop until reaching "uciok", which is
                # the last line SF outputs for the "uci" command.

    def get_evaluation(self) -> dict:
        """Searches to the specified depth and evaluates the current position

        Returns:
            A dictionary of the current advantage with "type" as "cp" (centipawns) or "mate" (mate in n moves)
        """

        if self._on_weaker_setting():
            self._weaker_setting_warning(
                """Note that even though you've set Stockfish to play on a weaker elo or skill level,"""
                + """ get_evaluation will still return full strength Stockfish's evaluation of the position."""
            )

        compare: int = (
            1 if self.get_turn_perspective() or ("w" in self.get_fen_position()) else -1
        )
        # If the user wants the evaluation specified relative to who is to move, this will be done.
        # Otherwise, the evaluation will be in terms of white's side (positive meaning advantage white,
        # negative meaning advantage black).
        self._go()
        evaluation: dict = dict()
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

    def get_static_eval(self) -> Optional[float]:
        """Sends the 'eval' command to stockfish to get the static evaluation. The current position is
           'directly' evaluated -- i.e., no search is involved.

        Returns:
            A float representing the static eval, unless one side is in check or checkmated,
            in which case None is returned.
        """

        # Stockfish gives the static eval from white's perspective:
        compare: int = (
            1
            if not self.get_turn_perspective() or ("w" in self.get_fen_position())
            else -1
        )
        self._put("eval")
        while True:
            text = self._read_line()
            if text.startswith("Final evaluation") or text.startswith(
                "Total Evaluation"
            ):
                splitted_text = text.split()
                eval = splitted_text[2]
                if eval == "none":
                    assert "(in check)" in text
                    return None
                else:
                    return float(eval) * compare

    def get_top_moves(
        self,
        num_top_moves: int = 5,
        verbose: bool = False,
        num_nodes: int = 0,
    ) -> List[dict]:
        """Returns info on the top moves in the position.

        Args:
            num_top_moves:
              The number of moves for which to return information, assuming there
              are at least that many legal moves.
              Default is 5.

            verbose:
              Option to include the full info from the engine in the returned dictionary,
              including seldepth, multipv, time, nodes, nps, and wdl if available.
              `Boolean`. Default is `False`.

            num_nodes:
              Option to search until a certain number of nodes have been searched, instead of depth.
              Default is 0.

        Returns:
            A list of dictionaries, where each dictionary contains keys for `Move`, `Centipawn`, and `Mate`.
            The corresponding value for either the `Centipawn` or `Mate` key will be `None`.
            If there are no moves in the position, an empty list is returned.

            If `verbose` is `True`, the dictionary will also include the following keys: `SelectiveDepth`, `Time`,
            `Nodes`, `NodesPerSecond`, `MultiPVLine`, and `WDL` (if available).

        Example:
            >>> moves = stockfish.get_top_moves(2, num_nodes=1000000, verbose=True)
        """
        if num_top_moves <= 0:
            raise ValueError("num_top_moves is not a positive number.")
        if self._on_weaker_setting():
            self._weaker_setting_warning(
                """Note that even though you've set Stockfish to play on a weaker elo or skill level,"""
                + """ get_top_moves will still return the top moves of full strength Stockfish."""
            )

        # remember global values
        old_multipv: int = self._parameters["MultiPV"]
        old_num_nodes: int = self._num_nodes

        # to get number of top moves, we use Stockfish's MultiPV option (i.e., multiple principal variations).
        # set MultiPV to num_top_moves requested
        if num_top_moves != self._parameters["MultiPV"]:
            self._set_option("MultiPV", num_top_moves)

        # start engine. will go until reaches self._depth or self._num_nodes
        if num_nodes == 0:
            self._go()
        else:
            self._num_nodes = num_nodes
            self._go_nodes()

        lines: List[List[str]] = []

        # parse output into a list of lists
        # this loop will run until Stockfish has finished evaluating the position
        while True:
            text = self._read_line()
            split_text = text.split(" ")
            lines.append(split_text)
            # The "bestmove" line is the last line of the evaluation.
            if split_text[0] == "bestmove":
                break

        # Stockfish is now done evaluating the position,
        # and the output is stored in the list 'lines'
        top_moves: List[dict] = []

        # set perspective of evaluations. if get_turn_perspective() is True, or white to move,
        # use Stockfish's values, otherwise invert values.
        perspective: int = (
            1 if self.get_turn_perspective() or ("w" in self.get_fen_position()) else -1
        )

        # loop through Stockfish output lines in reverse order
        for line in reversed(lines):
            # if the line is a "bestmove" line, and the best move is "(none)", then
            # there are no top moves, and we're done. otherwise, continue with next line
            if line[0] == "bestmove":
                if line[1] == "(none)":
                    top_moves = []
                    break
                continue

            # if the line has no relevant info, we're done
            if ("multipv" not in line) or ("depth" not in line):
                break

            # if we're searching depth and the line is not our desired depth, we're done
            if (num_nodes == 0) and (int(self._pick(line, "depth")) != self._depth):
                break

            # if we're searching nodes and the line has less than desired number of nodes, we're done
            if (num_nodes > 0) and (int(self._pick(line, "nodes")) < self._num_nodes):
                break

            move_evaluation: dict[str, Union[str, int, None]] = {
                # get move
                "Move": self._pick(line, "pv"),
                # get cp if available
                "Centipawn": int(self._pick(line, "cp")) * perspective
                if "cp" in line
                else None,
                # get mate if available
                "Mate": int(self._pick(line, "mate")) * perspective
                if "mate" in line
                else None,
            }

            # add more info if verbose
            if verbose:
                move_evaluation["Time"] = self._pick(line, "time")
                move_evaluation["Nodes"] = self._pick(line, "nodes")
                move_evaluation["MultiPVLine"] = self._pick(line, "multipv")
                move_evaluation["NodesPerSecond"] = self._pick(line, "nps")
                move_evaluation["SelectiveDepth"] = self._pick(line, "seldepth")

                # add wdl if available
                if self.does_current_engine_version_have_wdl_option():
                    move_evaluation["WDL"] = " ".join(
                        [
                            self._pick(line, "wdl", 1),
                            self._pick(line, "wdl", 2),
                            self._pick(line, "wdl", 3),
                        ][::perspective]
                    )

            # add move to list of top moves
            top_moves.insert(0, move_evaluation)

        # reset MultiPV to global value
        if old_multipv != self._parameters["MultiPV"]:
            self._set_option("MultiPV", old_multipv)

        # reset self._num_nodes to global value
        if old_num_nodes != self._num_nodes:
            self._num_nodes = old_num_nodes

        return top_moves

    def _pick(self, line: list[str], value: str = "", index: int = 1) -> str:
        return line[line.index(value) + index]

    def get_what_is_on_square(self, square: str) -> Optional[Piece]:
        """Returns what is on the specified square.

        Args:
            square:
                The coordinate of the square in question, eg. e4.

        Returns:
            Either one of the 12 enum members in the `Piece` enum, or the `None`
            object if the square is empty.

        Example:
            >>> piece = stockfish.get_what_is_on_square("e2")
        """

        file_letter: str = square[0].lower()
        rank_num: int = int(square[1])
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
        rank_visual: str = self.get_board_visual().splitlines()[17 - 2 * rank_num]
        piece_as_char: str = rank_visual[2 + (ord(file_letter) - ord("a")) * 4]
        return None if piece_as_char == " " else Stockfish.Piece(piece_as_char)

    def will_move_be_a_capture(self, move_value: str) -> Capture:
        """Returns whether the proposed move will be a direct capture,
           en passant, or not a capture at all.

        Args:
            move_value:
                The proposed move, in the notation that Stockfish uses.
                E.g., "e2e4", "g1f3", etc.

        Returns:
            One of the following members of the `Capture` enum:
            - DIRECT_CAPTURE if the move will be a direct capture.
            - EN_PASSANT if the move is a capture done with en passant.
            - NO_CAPTURE if the move does not capture anything.

        Example:
            >>> capture = stockfish.will_move_be_a_capture("e2e4")
        """
        if not self.is_move_correct(move_value):
            raise ValueError("The proposed move is not valid in the current position.")
        starting_square_piece: Optional[Stockfish.Piece] = self.get_what_is_on_square(
            move_value[:2]
        )
        ending_square_piece: Optional[Stockfish.Piece] = self.get_what_is_on_square(
            move_value[2:4]
        )
        if ending_square_piece is not None:
            if not self._parameters["UCI_Chess960"]:
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
        elif move_value[2:4] == self.get_fen_position().split()[
            3
        ] and starting_square_piece in [
            Stockfish.Piece.WHITE_PAWN,
            Stockfish.Piece.BLACK_PAWN,
        ]:
            return Stockfish.Capture.EN_PASSANT
        else:
            return Stockfish.Capture.NO_CAPTURE

    def get_stockfish_major_version(self) -> int:
        """Returns Stockfish engine major version.

        Returns:
            The major version of the Stockfish engine being used, eg. 15.
        """
        return self._stockfish_major_version

    def is_development_build_of_engine(self) -> bool:
        """Returns whether the version of Stockfish being used is a
           development build.

        Returns:
            `True` if the major version is a date, indicating Stockfish is a
            development build. E.g., 020122 is the major version of the Stockfish
            development build released on Jan 2, 2022. Otherwise `False` is
            returned (which means the engine is an official release of Stockfish).
        """
        return (
            self._stockfish_major_version >= 10109
            and self._stockfish_major_version <= 311299
        )

    def send_quit_command(self) -> None:
        """Sends the 'quit' command to the Stockfish engine, getting the process
        to stop."""

        if self._stockfish.poll() is None:
            self._put("quit")
            while self._stockfish.poll() is None:
                pass

    def __del__(self) -> None:
        Stockfish._del_counter += 1
        self.send_quit_command()

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

    class Capture(Enum):
        DIRECT_CAPTURE = "direct capture"
        EN_PASSANT = "en passant"
        NO_CAPTURE = "no capture"

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
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            if splitted_text[0] == "Nodes/second":
                return text


class StockfishException(Exception):
    pass
