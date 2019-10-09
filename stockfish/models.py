"""
    This module implements the Stockfish class.

    :copyright: (c) 2016 by Ilya Zhelyabuzhsky.
    :license: GPLv3, see LICENSE for more details.
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
        self, path: str = "stockfish", depth: int = 2, params: dict = None
    ) -> None:
        self.stockfish = subprocess.Popen(
            path, universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )

        self.__put("uci")

        self.depth = str(depth)
        self.info: str = ""

        if params is None:
            params = {}
        self.params = DEFAULT_STOCKFISH_PARAMS
        self.params.update(params)
        for name, value in list(self.params.items()):
            self.__set_option(name, value)

        self.__start_new_game()

    def __start_new_game(self) -> None:
        self.__put("ucinewgame")
        self.__is_ready()

    def __put(self, command: str) -> None:
        self.stockfish.stdin.write(f"{command}\n")
        self.stockfish.stdin.flush()

    def __set_option(self, name: str, value: Any) -> None:
        self.__put(f"setoption name {name} value {value}")
        self.__is_ready()

    def __is_ready(self) -> None:
        self.__put("isready")
        while True:
            if self.stockfish.stdout.readline().strip() == "readyok":
                return

    def __go(self) -> None:
        self.__put(f"go depth {self.depth}")

    @staticmethod
    def __convert_move_list_to_str(moves: List[str]) -> str:
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
        if moves is None:
            moves = []
        self.__put(f"position startpos moves {self.__convert_move_list_to_str(moves)}")

    def set_fen_position(self, fen_position: str) -> None:
        self.__start_new_game()
        self.__put(f"position fen {fen_position}")

    def get_best_move(self) -> Optional[str]:
        """Get best move with current position on the board.

        Returns:
            A string of move in algebraic notation or False, if it's a mate now.
        """
        self.__go()
        last_text: str = ""
        while True:
            text = self.stockfish.stdout.readline().strip()
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
        self.__put("go depth 1 searchmoves %s" % move_value)
        while True:
            text = self.stockfish.stdout.readline().strip()
            splitted_text = text.split(" ")
            if splitted_text[0] == "bestmove":
                if splitted_text[1] == "(none)":
                    return False
                else:
                    return True

    def __del__(self) -> None:
        self.stockfish.kill()
