"""
    stockfish.stockfish
    ~~~~~~~~~~~~~~~~~~~

    This module implemets ths Stockfish class.

    :copyright: (c) 2016 by Ilya Zhelyabuzhsky.
    :license: GPLv3, see LICENSE for more details.
"""

import subprocess


class Stockfish:
    """Integrates the Stockfish chess engine with Python."""

    def __init__(self, path=None, depth=2, param=None):
        if param is None:
            param = {}
        if path is None:
            path = "stockfish"
        self.stockfish = subprocess.Popen(
            path, universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )
        self.depth = str(depth)
        self.__put("uci")

        default_param = {
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

        default_param.update(param)
        self.param = default_param
        for name, value in list(default_param.items()):
            self.__set_option(name, value)

        self.__start_new_game()

    def __start_new_game(self):
        self.__put("ucinewgame")
        self.__isready()

    def __put(self, command):
        self.stockfish.stdin.write(command + "\n")
        self.stockfish.stdin.flush()

    def __set_option(self, optionname, value):
        self.__put("setoption name %s value %s" % (optionname, str(value)))
        stdout = self.__isready()
        if stdout.find("No such") >= 0:
            print("stockfish was unable to set option %s" % optionname)

    def __isready(self):
        self.__put("isready")
        while True:
            text = self.stockfish.stdout.readline().strip()
            if text == "readyok":
                return text

    def __go(self):
        self.__put("go depth %s" % self.depth)

    @staticmethod
    def __convert_move_list_to_str(moves):
        result = ""
        for move in moves:
            result += move + " "
        return result.strip()

    def set_position(self, moves=None):
        """Sets current board positions.

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
        self.__put(
            "position startpos moves %s" % self.__convert_move_list_to_str(moves)
        )

    def set_fen_position(self, fen_position):
        self.__put("position fen " + fen_position)

    def get_best_move(self):
        """Get best move with current position on the board.

        Returns:
            A string of move in algebraic notation or False, if it's a mate now.
        """
        self.__go()
        while True:
            text = self.stockfish.stdout.readline().strip()
            split_text = text.split(" ")
            if split_text[0] == "bestmove":
                if split_text[1] == "(none)":
                    return False
                return split_text[1]

    def is_move_correct(self, move_value):
        """Checks new move.

        Args:
            move_value: New move value in algebraic notation.

        Returns:
            True, if new move is correct, else False.
        """
        self.__put("go depth 1 searchmoves %s" % move_value)
        while True:
            text = self.stockfish.stdout.readline().strip()
            split_text = text.split(" ")
            if split_text[0] == "bestmove":
                if split_text[1] == "(none)":
                    return False
                else:
                    return True

    def __del__(self):
        self.stockfish.kill()
