"""
    This module implements the Stockfish class.

    :copyright: (c) 2016-2020 by Ilya Zhelyabuzhsky.
    :license: MIT, see LICENSE for more details.
"""

import subprocess
from typing import Any, List, Optional

DEFAULT_STOCKFISH_PARAMS = {
    "Write Debug Log": "false",
    "Contempt": 0,
    "Min Split Depth": 0,
    "Threads": 1,
    "Ponder": "false",
    "Hash": 16,
    "MultiPV": 1,
    "Skill Level": 20,
    "Move Overhead": 30,
    "Minimum Thinking Time": 20,
    "Slow Mover": 80,
    "UCI_Chess960": "false",
}


class Stockfish:
    """Integrates the Stockfish chess engine with Python."""

    def __init__(
        self, path: str = "stockfish", depth: int = 2, parameters: dict = None
    ) -> None:
        self.stockfish = subprocess.Popen(
            path, universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )

        self._put("uci")

        self.depth = str(depth)
        self.info: str = ""

        if parameters is None:
            parameters = {}
        self._parameters = DEFAULT_STOCKFISH_PARAMS
        self._parameters.update(parameters)
        for name, value in list(self._parameters.items()):
            self._set_option(name, value)

        self._start_new_game()

    def get_parameters(self) -> dict:
        """Returns current board position.

        Returns:
            Dictionary of current Stockfish engine's parameters.
        """
        return self._parameters

    def _start_new_game(self) -> None:
        self._put("ucinewgame")
        self._is_ready()
        self.info = ""

    def _put(self, command: str) -> None:
        if not self.stockfish.stdin:
            raise BrokenPipeError()
        self.stockfish.stdin.write(f"{command}\n")
        self.stockfish.stdin.flush()

    def _read_line(self) -> str:
        if not self.stockfish.stdout:
            raise BrokenPipeError()
        return self.stockfish.stdout.readline().strip()

    def _set_option(self, name: str, value: Any) -> None:
        self._put(f"setoption name {name} value {value}")
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

    @staticmethod
    def _convert_move_list_to_str(moves: List[str]) -> str:
        result = ""
        for move in moves:
            result += f"{move} "
        return result.strip()

    def set_position(self, moves: List[str] = None) -> None:
        """Sets current board position.

        Args:
            moves: A list of moves to set this position on the board.
                Must be in full algebraic notation.
                example:
                ['e2e4', 'e7e5']

        Returns:
            None
        """
        self._start_new_game()
        if moves is None:
            moves = []
        self._put(f"position startpos moves {self._convert_move_list_to_str(moves)}")

    def get_board_visual(self) -> str:
        """ Get a visual representation of the current board position 
            Note: "d" is a stockfish only command

        Args:

        Returns:
            String of visual representation of the chessboard with its pieces in current position
        """
        self._put("d")
        board_rep = ""
        count_lines = 0
        while count_lines < 17:
            board_str = self._read_line()
            if "+" in board_str or "|" in board_str:
                count_lines += 1
                board_rep += f"{board_str}\n"
        return board_rep

    def get_fen_position(self) -> str:
        """ Get current board position in Forsyth–Edwards notation (FEN).

        Args:

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
            skill_level: Skill Level option between 0 (weakest level) and 20 (full strength)

        Returns:
            None
        """
        self._set_option("Skill Level", skill_level)
        self._parameters.update({"Skill Level": skill_level})

    def set_fen_position(self, fen_position: str) -> None:
        """Sets current board position in Forsyth–Edwards notation (FEN).

        Args:
            fen_position: FEN string of board position.

        Returns:
            None
        """
        self._start_new_game()
        self._put(f"position fen {fen_position}")

    def get_best_move(self) -> Optional[str]:
        """Get best move with current position on the board.

        Returns:
            A string of move in algebraic notation or False, if it's a mate now.
        """
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
        """Get best move with current position on the board after a determined time

        Args:
            time: Time for stockfish to determine best move in milliseconds (int)

        Returns:
            A string of move in algebraic notation or False, if it's a mate now.
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
            move_value: New move value in algebraic notation.

        Returns:
            True, if new move is correct, else False.
        """
        self._put(f"go depth 1 searchmoves {move_value}")
        while True:
            text = self._read_line()
            splitted_text = text.split(" ")
            if splitted_text[0] == "bestmove":
                if splitted_text[1] == "(none)":
                    return False
                else:
                    return True

    def get_evaluation(self) -> dict:
        """Evaluates current position

        Returns:
            A dictionary of the current advantage with "type" as "cp" (centipawns) or "mate" (checkmate in)
        """

        evaluation = dict()
        fen = self.get_fen_position()
        if "w" in fen:  # w can only be in FEN if it is whites move
            compare = 1
        else:  # stockfish shows advantage relative to current player, convention is to do white positive
            compare = -1
        self._put("position " + fen + "\n go")
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

    def set_depth(self, depth_value: int = 2) -> None:
        """Sets current depth of stockfish engine.

        Args:
            depth_value: Depth option higher than 1

        Returns:
            None
        """
        self.depth = str(depth_value)

    def __del__(self) -> None:
        self.stockfish.kill()
