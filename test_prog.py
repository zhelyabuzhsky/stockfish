from stockfish import Stockfish
s1 = Stockfish("/home/tvivek/Downloads/stockfish_13_linux_x64/stockfish_13_linux_x64");
s2 = Stockfish("/home/tvivek/Downloads/stockfish_13_linux_x64/stockfish_13_linux_x64");

assert s1 is not s2

arg1 = s1.get_parameters()
arg2 = s2.get_parameters()

assert arg1 == arg2

s1.set_skill_level(1)

arg1 = s1.get_parameters()
arg2 = s2.get_parameters()

assert arg1 != arg2
