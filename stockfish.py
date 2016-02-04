import subprocess


class Stockfish:

    def __init__(self, path=None, depth=2, param=None):
        if param is None:
            param = {}
        if path is None:
            path = 'stockfish'
        self.stockfish = subprocess.Popen(
            path,
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        self.depth = str(depth)
        self.__put('uci')

        default_param = {
            'Write Debug Log': 'false',
            'Contempt Factor': 0,
            'Contempt': 0,
            'Min Split Depth': 0,
            'Threads': 1,
            'Ponder': 'false',
            'Hash': 16,
            'MultiPV': 1,
            'Skill Level': 20,
            'Move Overhead': 30,
            'Minimum Thinking Time': 20,
            'Slow Mover': 80,
            'UCI_Chess960': 'false'
        }

        default_param.update(param)
        self.param = default_param
        for name, value in list(default_param.items()):
            self.__set_option(name, value)

        self.__start_new_game()

    def __start_new_game(self):
        self.__put('ucinewgame')
        self.__isready()

    def __put(self, command):
        self.stockfish.stdin.write(command + '\n')
        self.stockfish.stdin.flush()

    def __set_option(self, optionname, value):
        self.__put('setoption name %s value %s' % (optionname, str(value)))
        stdout = self.__isready()
        if stdout.find('No such') >= 0:
            print("stockfish was unable to set option %s" % optionname)

    def set_position(self, moves=None):
        """
        :param moves: list of moves (i.e. ['e2e4', 'e7e5', ...]), must be in full algebraic notation.
        """
        if moves is None:
            moves = []
        self.__put('position startpos moves %s' %
                   self.__convert_move_list_to_str(moves))
        self.__isready()

    def __go(self):
        self.__put('go depth %s' % self.depth)

    @staticmethod
    def __convert_move_list_to_str(moves):
        result = ''
        for move in moves:
            result += move + ' '
        return result.strip()

    def get_best_move(self):
        self.__go()
        while True:
            text = self.stockfish.stdout.readline().strip()
            split_text = text.split(' ')
            if split_text[0] == 'bestmove':
                return split_text[1]

    def __isready(self):
        self.__put('isready')
        while True:
            text = self.stockfish.stdout.readline().strip()
            if text == 'readyok':
                return text
