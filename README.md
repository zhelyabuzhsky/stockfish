# Stockfish
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
    "Ponder": "false",
    "Hash": 16, # Default size is 16 MB. It's recommended that you increase this value, but keep it as some power of 2. E.g., if you're fine using 2 GB of RAM, set Hash to 2048 (11th power of 2).
    "MultiPV": 1,
    "Skill Level": 20,
    "Move Overhead": 10,
    "Minimum Thinking Time": 20,
    "Slow Mover": 100,
    "UCI_Chess960": "false",
    "UCI_LimitStrength": "false",
    "UCI_Elo": 1350
}
```

You can change them, as well as the default search depth, during your Stockfish class initialization:
```python
stockfish = Stockfish(path="/Users/zhelyabuzhsky/Work/stockfish/stockfish-9-64", depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 30})
```

These parameters can also be updated at any time by calling the "update_engine_parameters" function:
```python
stockfish.update_engine_parameters({"Hash": 2048, "UCI_Chess960": "true"}) # Gets stockfish to use a 2GB hash table, and also to play Chess960.
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

### Update position by making a sequence of moves from the current position
```python
stockfish.make_moves_from_current_position(["g4d7", "a8b8", "f1d1"])
```

### Set position by Forsyth–Edwards Notation (FEN)
If you'd like to first check if your fen is valid, call the is_fen_valid() function below.  
Also, if you want to play Chess960, it's recommended you first update the "UCI_Chess960" engine parameter to be "true", before calling set_fen_position.
```python
stockfish.set_fen_position("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
```

### Check whether the given FEN is valid
This function returns a bool saying whether the passed in FEN is valid (both syntax wise and whether the position represented is legal).  
The function isn't perfect and won't catch all cases, but generally it should return the correct answer.
For example, one exception is positions which are legal, but have no legal moves. 
I.e., for checkmates and stalemates, this function will incorrectly say the fen is invalid.
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

### Check is move correct with current position
```python
stockfish.is_move_correct('a2a3')
```
```text
True
```

### Get info on the top n moves
```python
stockfish.get_top_moves(3)
```
```text
[
    {'Move': 'f5h7', 'Centipawn': None, 'Mate': 1},
    {'Move': 'f5d7', 'Centipawn': 713, 'Mate': None},
    {'Move': 'f5h5', 'Centipawn': -31, 'Mate': None}
]
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

### Set current engine's skill level (ignoring ELO rating)
```python
stockfish.set_skill_level(15)
```

### Set current engine's ELO rating (ignoring skill level)
```python
stockfish.set_elo_rating(1350)
```

### Set current engine's depth
```python
stockfish.set_depth(15)
```

### Get current engine's parameters
```python
stockfish.get_parameters()
```
```text
{
    "Debug Log File": "",
    "Contempt": 0,
    "Min Split Depth": 0,
    "Threads": 1,
    "Ponder": "false",
    "Hash": 16,
    "MultiPV": 1,
    "Skill Level": 20,
    "Move Overhead": 10,
    "Minimum Thinking Time": 20,
    "Slow Mover": 100,
    "UCI_Chess960": "false",
    "UCI_LimitStrength": "false",
    "UCI_Elo": 1350
}
```

### Reset the engine's parameters to the default
```python
stockfish.reset_engine_parameters()
```

### Get current board position in Forsyth–Edwards notation (FEN)
```python
stockfish.get_fen_position()
```
```text
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

### Get current board visual
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

### Get current board evaluation in centipawns or mate in x
```python 
stockfish.get_evaluation()
```
Positive is advantage white, negative is advantage black
```text
{"type":"cp", "value":12}
{"type":"mate", "value":-3}
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

### Get current major version of stockfish engine
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

### Find what is on a certain square
If the square is empty, the None object is returned. Otherwise, one of 12 enum members of a custom  
Stockfish.Piece enum will be returned. Each of the 12 members of this enum is named in the following pattern:  
*colour* followed by *underscore* followed by *piece name*, where the colour and piece name are in all caps.  
For example, say the current position is the starting position:  
```python
stockfish.get_what_is_on_square("e1") # returns Stockfish.Piece.WHITE_KING
stockfish.get_what_is_on_square("d8") # returns Stockfish.Piece.BLACK_QUEEN
stockfish.get_what_is_on_square("h2") # returns Stockfish.Piece.WHITE_PAWN
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

### StockfishException

The `StockfishException` is a newly defined Exception type. It is thrown when the underlying Stockfish process created by the wrapper crashes. This can happen when an incorrect input like an invalid FEN (for example ```8/8/8/3k4/3K4/8/8/8 w - - 0 1``` with both kings next to each other) is given to Stockfish. \
Not all invalid inputs will lead to a `StockfishException`, but only those which cause the Stockfish process to crash. \
To handle a `StockfishException` when using this library, import the `StockfishException` from the library and use a `try/except`-block:
```python
from stockfish import StockfishException

try:
    # Evaluation routine

except StockfishException:
    # Error handling
```

## Testing
```bash
$ python setup.py test
```

## Security
If you discover any security related issues, please email zhelyabuzhsky@icloud.com instead of using the issue tracker.

## Credits
- [Ilya Zhelyabuzhsky](https://github.com/zhelyabuzhsky)
- [All Contributors](https://github.com/zhelyabuzhsky/stockfish/graphs/contributors)

## License
MIT License. Please see [License File](https://github.com/zhelyabuzhsky/stockfish/blob/master/LICENSE) for more information.
