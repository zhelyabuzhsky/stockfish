# Stockfish

> **Note**
> This section refers to the technical application. If you are looking for information regarding the status of this project and the original repo, please look [here](https://github.com/py-stockfish/stockfish/tree/master#status-of-the-project).

Implements an easy-to-use Stockfish class to integrates the Stockfish chess engine with Python.

## Install

```bash
$ pip install stockfish
```

#### Ubuntu

```bash
$ sudo apt install stockfish
```

#### Mac OS

```bash
$ brew install stockfish
```

## API Documentation

See [API Documentation](https://py-stockfish.github.io/stockfish/) for more information.

## Features and usage examples

### Initialize Stockfish class

You should install the stockfish engine in your operating system globally or specify path to binary file in class constructor

```python
from stockfish import Stockfish

stockfish = Stockfish(path="/Users/zhelyabuzhsky/Work/stockfish/stockfish-9-64")
```

There are some default engine settings used by this wrapper. For increasing Stockfish's strength and speed, the "Threads" and "Hash" parameters can be modified.

```python
{
    "Debug Log File": "",
    "Contempt": 0,
    "Min Split Depth": 0,
    "Threads": 1, # More threads will make the engine stronger, but should be kept at less than the number of logical processors on your computer.
    "Ponder": False,
    "Hash": 16, # Default size is 16 MB. It's recommended that you increase this value, but keep it as some power of 2. E.g., if you're fine using 2 GB of RAM, set Hash to 2048 (11th power of 2).
    "MultiPV": 1,
    "Skill Level": 20,
    "Move Overhead": 10,
    "Minimum Thinking Time": 20,
    "Slow Mover": 100,
    "UCI_Chess960": False,
    "UCI_LimitStrength": False,
    "UCI_Elo": 1350
}
```

You can change them, as well as the search depth, during your Stockfish class initialization:

```python
stockfish = Stockfish(path="/Users/zhelyabuzhsky/Work/stockfish/stockfish-9-64", depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 30})
```

These parameters can also be updated at any time by calling the "update_engine_parameters" function:

```python
stockfish.update_engine_parameters({"Hash": 2048, "UCI_Chess960": True}) # Gets stockfish to use a 2GB hash table, and also to play Chess960.
```

As for the depth, it can also be updated, by using the following function. Note that if you don't set depth to a value yourself, the python module will initialize it to 15 by default.

```python
stockfish.set_depth(12)
```

When you're done using the Stockfish engine process, you can send the "quit" uci command to it with:

```python
stockfish.send_quit_command()
```

The `__del__()` method of the Stockfish class will call send_quit_command(), but it's technically not guaranteed python will call `__del__()` when the Stockfish object goes out of scope. So even though it'll probably not be needed, it doesn't hurt to call send_quit_command() yourself.

### Set position by a sequence of moves from the starting position

```python
stockfish.set_position(["e2e4", "e7e6"])
```
If you'd just like to set up the starting position without making any moves from it, just call this function without sending an argument:
```python
stockfish.set_position()
```

### Update position by making a sequence of moves from the current position

Function takes a list of strings as its argument. Each string represents a move, and must have the format of the starting coordinate followed by the ending coordinate. If a move leads to a pawn promoting, then an additional character must be appended at the end (to indicate what piece the pawn promotes into).  
Other types of special moves (e.g., checks, captures, checkmates, en passants) do not need any special notation; the starting coordinate followed by the ending coordinate is all the information that's needed. Note that castling is represented by the starting coordinate of the king followed by the ending coordinate of the king. So "e1g1" would be used for white castling kingside, assuming the white king is still on e1 and castling is legal.  
Example call (assume in the current position, it is White's turn):
```python
stockfish.make_moves_from_current_position(["g4d7", "a8b8", "f1d1", "b2b1q"]) # Moves the white piece on g4 to d7, then the black piece on a8 to b8, then the white piece on f1 to d1, and finally pushes the black b2-pawn to b1, promoting it into a queen.
```

### Set position by Forsyth–Edwards Notation (FEN)

Note that if you want to play Chess960, it's recommended you first update the "UCI_Chess960" engine parameter to be True, before calling set_fen_position.

```python
stockfish.set_fen_position("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
```

### Check whether the given FEN is valid

This function returns a bool saying whether the passed in FEN is valid (both syntax wise and whether the position represented is legal).  
The function isn't perfect and won't catch all cases, but generally it should return the correct answer.
For example, one exception is positions which are legal, but have no legal moves.
I.e., for checkmates and stalemates, this function will incorrectly say the fen is invalid.


Note that the function checks whether a position is legal by temporarily creating a new Stockfish process, and
then seeing if it can return a best move (and also not crash). Whatever the outcome may be though, this
temporary SF process should terminate after the function call.

```python
stockfish.is_fen_valid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
```

```text
True
```

```python
stockfish.is_fen_valid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -") # will return False, in this case because the FEN is missing two of the six required fields.
```

```text
False
```

### Get best move

```python
stockfish.get_best_move()
```

```text
d2d4
```

It's possible to specify remaining time on black and/or white clock. Time is in milliseconds.

```python
stockfish.get_best_move(wtime=1000, btime=1000)
```

### Get best move based on a time constraint

```python
stockfish.get_best_move_time(1000)
```

Time constraint is in milliseconds

```text
e2e4
```

### Check if a move is legal in the current position

Returns True if the passed in move is legal in the current position.

```python
stockfish.is_move_correct('a2a3')
```

```text
True
```

### Get info on the top n moves

Returns a list of dictionaries, where each dictionary represents a move's info. Each dictionary will contain a value for the 'Move' key, and either the 'Centipawn' or 'Mate' value will be a number (the other will be None).
Positive values mean advantage white, negative advantage black (unless you're using the turn perspective setting).

Positive values mean advantage White, negative values mean advantage Black (unless you're using the turn perspective option, in which case positive is for the side to move). 

Note that if you have stockfish on a weaker elo or skill level setting, the top moves returned by this
function will still be for full strength.

Let's consider an example where Black is to move, and the top 3 moves are a mate, winning material, or being slightly worse. We'll assume the turn perspective setting is off.

```python
stockfish.get_top_moves(3)
# [
#   {'Move': 'f5h3', 'Centipawn': None, 'Mate': -1}, # The move f5h3 leads to a mate in 1 for Black.
#   {'Move': 'f5d7', 'Centipawn': -713, 'Mate': None}, # f5d7 leads to an evaluation of 7.13 in Black's favour.
#   {'Move': 'f5h5', 'Centipawn': 31, 'Mate': None} # f5h5 leads to an evaluation of 0.31 in White's favour.
# ]
```

Optional parameter `verbose` (default `False`) specifies whether to include the full info from the engine in the returned dictionary, including SelectiveDepth, Nodes, NodesPerSecond, Time, MultiPVLine, and WDL if available.

```py
stockfish.get_top_moves(1, verbose=True)
# [{
#   "Move":"d6e7",
#   "Centipawn":-408,
#   "Mate":"None",
#   "Nodes":"2767506",
#   "NodesPerSecond":"526442",
#   "Time":"5257",
#   "SelectiveDepth":"31",
#   "MultiPVLine":"1",
#   "WDL":"0 0 1000"
# }]
```

Optional parameter `num_nodes` specifies the number of nodes to search. If num_nodes is 0, then the engine will search until the configured depth is reached.

### Set perspective of the evaluation

You can set the perspective of the evaluation to be from the perspective of the side to move, or from the perspective of White. Currently this setting only applies to `get_top_moves()`.

```py
# Set the perspective of the evaluation to be from the point of view of the side to move
stockfish.set_turn_perspective(True)

# Set the perspective of the evaluation to be from White's perspective
stockfish.set_turn_perspective(False)

# Get the current perspective of the evaluation
is_turn_perspective = stockfish.get_turn_perspective()

```

### Get current board evaluation in centipawns or mate in x
```python 
stockfish.get_evaluation()
```

If turn perspective if off, then positive is advantage white, negative is advantage black.
Otherwise, positive is for the side to move.

```text
{"type":"cp", "value":12} # This being the return value would mean White is better by 0.12.

{"type":"mate", "value":-3} # This being the return value would mean Black can checkmate in 3.
```

### Get Stockfish's win/draw/loss stats for the side to move in the current position

Before calling this function, it is recommended that you first check if your version of Stockfish is recent enough to display WDL stats. To do this,  
use the "does_current_engine_version_have_wdl_option()" function below.

```python
stockfish.get_wdl_stats()
```

```text
[87, 894, 19]
```

### Find if your version of Stockfish is recent enough to display WDL stats

```python
stockfish.does_current_engine_version_have_wdl_option()
```

```text
True
```

### Set the engine's skill level (ignoring ELO rating)

```python
stockfish.set_skill_level(15)
```

### Set the engine's ELO rating (ignoring skill level)

```python
stockfish.set_elo_rating(1350)
```

### Put the engine back to full strength (if you've previously lowered the ELO or skill level)
```python
stockfish.resume_full_strength()
```

### Set the engine's search depth

```python
stockfish.set_depth(15)
```

### Get the engine's current parameters

Returns a deep copy of the dictionary storing the engine's current parameters.

```python
stockfish.get_engine_parameters()
```

```text
{
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
    "UCI_Elo": 1350
}

### Reset the engine's parameters to the default

```python
stockfish.reset_engine_parameters()
```

### Get the current board position in Forsyth–Edwards notation (FEN)

```python
stockfish.get_fen_position()
```

```text
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

### Get the current board visual

```python
stockfish.get_board_visual()
```

```text
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

This function has an optional boolean (True by default) as a parameter that indicates whether the board should be seen from the view of white. So it is possible to get the board from black's point of view like this:

```python
stockfish.get_board_visual(False)
```

```text
+---+---+---+---+---+---+---+---+
| R | N | B | K | Q | B | N | R | 1
+---+---+---+---+---+---+---+---+
| P | P | P | P | P | P | P | P | 2
+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |   | 3
+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |   | 4
+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |   | 5
+---+---+---+---+---+---+---+---+
|   |   |   |   |   |   |   |   | 6
+---+---+---+---+---+---+---+---+
| p | p | p | p | p | p | p | p | 7
+---+---+---+---+---+---+---+---+
| r | n | b | k | q | b | n | r | 8
+---+---+---+---+---+---+---+---+
  h   g   f   e   d   c   b   a
```

### Get the current position's evaluation in centipawns or mate in x

```python
stockfish.get_evaluation()
```

Stockfish searches to the specified depth and evaluates the current position.
A dictionary is returned representing the evaluation. Two example return values:

```text
{"type":"cp", "value":12}

{"type":"mate", "value":-3}
```

If stockfish.get_turn_perspective() is True, then the eval value is relative to the side to move.
Otherwise, positive is advantage white, negative is advantage black.

### Get the current position's 'static evaluation'

```python
stockfish.get_static_eval()
```

Sends the 'eval' command to Stockfish. This will get it to 'directly' evaluate the current position 
(i.e., no search is involved), and output a float value (not a whole number centipawn).

If one side is in check or mated, recent versions of Stockfish will output 'none' for the static eval.
In this case, the function will return None.

Some example return values:

```text
-5.27

0.28

None
```

### Run benchmark

#### BenchmarkParameters

```python
params = BenchmarkParameters(**kwargs)
```

parameters required to run the benchmark function. kwargs can be used to set custom values.

```text
ttSize: range(1,128001)
threads: range(1,513)
limit: range(1,10001)
fenFile: "path/to/file.fen"
limitType: "depth", "perft", "nodes", "movetime"
evalType: "mixed", "classical", "NNUE"
```

```python
stockfish.benchmark(params)
```

This will run the bench command with BenchmarkParameters.
It is an additional custom non-UCI command, mainly for debugging.
Do not use this command during a search!

### Get the major version of the stockfish engine being used

E.g., if the engine being used is Stockfish 14.1 or Stockfish 14, then the function would return 14.
Meanwhile, if a development build of the engine is being used (not an official release), then the function returns an
int with 5 or 6 digits, representing the date the engine was compiled on.
For example, 20122 is returned for the development build compiled on January 2, 2022.

```python
stockfish.get_stockfish_major_version()
```

```text
15
```

### Find if the version of Stockfish being used is a development build

```python
stockfish.is_development_build_of_engine()
```

```text
False
```

### Send the "ucinewgame" command to the Stockfish engine process. 
The main effect this command has is clearing SF's transposition table, and for most use cases there's no need to do this. Frequently sending this command can end up being a bottleneck on performance.
```python
stockfish.send_ucinewgame_command()
```

### Find what is on a certain square

If the square is empty, the None object is returned. Otherwise, one of 12 enum members of a custom  
Stockfish.Piece enum will be returned. Each of the 12 members of this enum is named in the following pattern:  
_colour_ followed by _underscore_ followed by _piece name_, where the colour and piece name are in all caps.  
The value of each enum member is a char representing the piece (uppercase is white, lowercase is black).  
For white, it will be one of "P", "N", "B", "R", "Q", or "K". For black the same chars, except lowercase.  
For example, say the current position is the starting position:

```python
stockfish.get_what_is_on_square("e1") # returns Stockfish.Piece.WHITE_KING
stockfish.get_what_is_on_square("e1").value # result is "K"
stockfish.get_what_is_on_square("d8") # returns Stockfish.Piece.BLACK_QUEEN
stockfish.get_what_is_on_square("d8").value # result is "q"
stockfish.get_what_is_on_square("h2") # returns Stockfish.Piece.WHITE_PAWN
stockfish.get_what_is_on_square("h2").value # result is "P"
stockfish.get_what_is_on_square("g8") # returns Stockfish.Piece.BLACK_KNIGHT
stockfish.get_what_is_on_square("g8").value # result is "n"
stockfish.get_what_is_on_square("b5") # returns None
```

### Find if a move will be a capture (and if so, what type of capture)

The argument must be a string that represents the move, using the notation that Stockfish uses (i.e., the coordinate of the starting square followed by the coordinate of the ending square).  
The function will return one of the following enum members from a custom Stockfish.Capture enum: DIRECT_CAPTURE, EN_PASSANT, or NO_CAPTURE.  
For example, say the current position is the one after 1.e4 Nf6 2.Nc3 e6 3.e5 d5.

```python
stockfish.will_move_be_a_capture("c3d5")  # returns Stockfish.Capture.DIRECT_CAPTURE
stockfish.will_move_be_a_capture("e5f6")  # returns Stockfish.Capture.DIRECT_CAPTURE
stockfish.will_move_be_a_capture("e5d6")  # returns Stockfish.Capture.EN_PASSANT
stockfish.will_move_be_a_capture("f1e2")  # returns Stockfish.Capture.NO_CAPTURE
```

### Convert human-style notation into the notation Stockfish uses
The argument is a string representing the move, written in some form that's used by humans. E.g., for using an e4-pawn to capture on d5, a string like
"e4xd5" or "exd5" could be sent in as a valid argument. The function would then return "e4d5".
```python
stockfish.convert_human_notation_to_sf_notation("e4xd5") # returns "e4d5"
```
For advancing a pawn (e.g., e4-pawn to e5), both "e5" and "e4e5" would be valid arguments to the function. For kingside castling, "0-0", "00", "O-O", "OO" all work (the function's return value for each would be "e1g1").
Or, say there are two rooks on a5 and b6, and an enemy piece on a6. The following would all be treated as valid "human-style" notations for the a5-rook capturing on a6: "Raxa6", "R5xa6", "a5xa6". Note that "Raa6" and "R5a6" wouldn't be valid "human-style" notations here, since the move is a capture but there isn't an 'x' indicating this. If an invalid argument (bad syntax, or an illegal move) is sent to the function, a ValueError will be raised.
```python
stockfish.convert_human_notation_to_sf_notation("Raxa6") # returns "a5a6"
```
Also, if the move passed to the function is already in Stockfish notation (beginning coordinate followed by ending coordinate, with the promotion piece type if applicable), then it's treated as valid and just returned as is. E.g., in the above case, passing in "a5a6" would also be a valid input (despite not having an 'x' to signify a capture), and the return value is the same "a5a6".

### Get the number of pieces in the current position
```python
stockfish.get_num_pieces() # Would return the int 32, if say the current position were the starting chess position.
```
This function also has 3 optional arguments, which can be used to give you more specialized info. They are:
  * file_range: List\[str\]  
    *  This parameter is a list of 2 strings, where each string is a letter between "a" and "h" inclusive. The two strings represent the start and end of the range of files which will be included for the count. The default value is \["a", "h"\], which gets the function to count pieces on all 8 of the board's files.  
  * rank_range: List\[int\]  
    * Similarly, this parameter allows you to only count on specific ranks, if you wish. The default value is \[1, 8\], which gets the function to count on all 8 ranks. If you specify a value for this parameter, make it a list of length 2, where the elements are both ints between 1 and 8 inclusive. E.g., rank_range=\[2, 5\] would be to count on just ranks 2, 3, 4, and 5.  
  * pieces_to_count: List  
    * This parameter allows you to control which pieces are counted. The default value for this parameter is \["P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k"\], which gets the function to count all types of pieces. If, for example, you only want to count pawns and white rooks, you can send in \["P", "p", "R"\]. The list can also contain members of the Stockfish.Piece enum, if you'd prefer to use this custom enum of the Stockfish class. E.g., sending in \[Stockfish.Piece.WHITE_PAWN, Stockfish.Piece.BLACK_PAWN, Stockfish.Piece.WHITE_ROOK\] as the argument will yield the same behaviour.  

Some example calls to the function (let's assume the current position is the starting chess position):  
```python
stockfish.get_num_pieces(rank_range=[2, 2]) # returns 8, since the function counts all pieces on just the second rank.
stockfish.get_num_pieces(file_range=["a", "d"], pieces_to_count=["N", "P", "p"]) # returns 9, since between files a-d, there is one white knight, four white pawns, and four black pawns.
stockfish.get_num_pieces(file_range=["d", "e"], rank_range=[1, 2]) # returns 4, since in this area there is a white king, queen, and two pawns.
stockfish.get_num_pieces(rank_range=[1, 6], pieces_to_count=[Stockfish.Piece.BLACK_PAWN]) # returns 0, since currently all the black pawns are on the 7th rank.
stockfish.get_num_pieces(pieces_to_count=["R", "r"]) # returns 4, since there are 4 rooks on the board.
```

### StockfishException

The `StockfishException` is a newly defined Exception type. It is thrown when the underlying Stockfish process created by the wrapper crashes. This can happen when an incorrect input like an invalid FEN (for example `8/8/8/3k4/3K4/8/8/8 w - - 0 1` with both kings next to each other) is given to Stockfish. \
Not all invalid inputs will lead to a `StockfishException`, but only those which cause the Stockfish process to crash. \
To handle a `StockfishException` when using this library, import the `StockfishException` from the library and use a `try/except`-block:

```python
from stockfish import StockfishException

try:
    # Evaluation routine

except StockfishException:
    # Error handling
```

### Debug view

You can (de-)activate the debug view option with the `set_debug_view` function. Like this you can see all communication between the engine and the library.

```python
stockfish.set_debug_view(True)
```

## Testing

```bash
$ python setup.py test
```
To skip some of the slower tests, run:
```bash
$ python setup.py skip_slow_tests
```

## Security

If you discover any security related issues, please report it via the [Private vulnerability reporting](https://github.com/py-stockfish/stockfish/security) instead of using the issue tracker.

## Status of the project

> **Note**
> This is just a brief summary. For more information, please look [here](https://github.com/zhelyabuzhsky/stockfish/issues/130).

Due to the [unfortunate death](https://github.com/zhelyabuzhsky/stockfish/pull/112#issuecomment-1367800036) of [Ilya Zhelyabuzhsky](https://github.com/zhelyabuzhsky), the original [repo](https://github.com/zhelyabuzhsky/stockfish) is no longer maintained. For this reason, this fork was created, which continues the project and is currently maintained by [johndoknjas](https://github.com/johndoknjas) and [kieferro](https://github.com/kieferro).
The official PyPi releases for the [Stockfish package](https://pypi.org/project/stockfish/) will also be created from this repo in the future.

Please submit all bug reports and PRs to this repo instead of the old one.

## Credits

- We want to sincerely thank [Ilya Zhelyabuzhsky](https://github.com/zhelyabuzhsky), the original founder of this project for writing and maintaining the code and for his contributions to the open source community.
- We also want to thank all the [other contributors](https://github.com/py-stockfish/stockfish/graphs/contributors) for working on this project.

## License

MIT License. Please see [License File](https://github.com/py-stockfish/stockfish/blob/master/LICENSE) for more information.
