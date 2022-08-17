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

You can change them, as well as the search depth, during your Stockfish class initialization:
```python
stockfish = Stockfish(path="/Users/zhelyabuzhsky/Work/stockfish/stockfish-9-64", depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 30})
```

These parameters can also be updated at any time by calling the "update_engine_parameters" function:
```python
stockfish.update_engine_parameters({"Hash": 2048, "UCI_Chess960": "true"}) # Gets stockfish to use a 2GB hash table, and also to play Chess960.
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
Returns True if the passed in move is legal in the current position.
```python
stockfish.is_move_correct('a2a3')
```
```text
True
```

### Get info on the top n moves
Returns a list of dictionaries, where each dictionary represents a move's info. Each dictionary will contain a value for the 'Move' key,
and either the 'Centipawn' or 'Mate' value will be a number (the other will be None). Positive values mean advantage for White, negative means
advantage for Black. E.g., 'Mate': 3 means that White can mate in three moves, 'Mate': -2 means Black mates in two moves, 'Centipawn': -20 means the
evaluation is -0.20 (0.20 advantage in Black's favour).
E.g., for an example position where White is to move, and the top moves are either a mate, winning material, or being slightly worse:
```python
stockfish.get_top_moves(3)
```
```text
[
    {'Move': 'f5h7', 'Centipawn': None, 'Mate': 1}, # the move f5h7 leads to a mate in 1
    {'Move': 'f5d7', 'Centipawn': 713, 'Mate': None}, # f5d7 leads to an evaluation of +7.13
    {'Move': 'f5h5', 'Centipawn': -31, 'Mate': None} # f5h5 leads to an evaluation of -0.31
]
```

### Get current board evaluation in centipawns or mate in x
```python 
stockfish.get_evaluation()
```
Positive is advantage white, negative is advantage black.
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

### Set current engine's skill level (ignoring ELO rating)
```python
stockfish.set_skill_level(15)
```

### Set current engine's ELO rating (ignoring skill level)
```python
stockfish.set_elo_rating(1350)
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

### Send the "ucinewgame" command to the Stockfish engine process. 
The main effect this command has is clearing SF's transposition table, and for most use cases it's probably not worth doing this. Frequently sending this command can end up being a bottleneck on performance.
```python
stockfish.send_ucinewgame_command()
```

### Find what is on a certain square
If the square is empty, the None object is returned. Otherwise, one of 12 enum members of a custom  
Stockfish.Piece enum will be returned. Each of the 12 members of this enum is named in the following pattern:  
*colour* followed by *underscore* followed by *piece name*, where the colour and piece name are in all caps.  
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
  * specific_file: str  
    * The default value is just the None object, which gets the function to not deal with any one file, but all 8 of them. If you send a value to this parameter, it should be a string representing a letter between "a" and "h". This will get the function to only count on the specified file.  
  * specific_rank: int  
    * Similarly, this parameter allows you to only count on a specific rank, if you wish. The default is again None, which gets the function to count on all the board's 8 ranks. If you send in a value, make it an int between 1 and 8 inclusive.  
  * pieces_to_count: List  
    * This parameter allows you to control which pieces are counted. The default value for this parameter is \["P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k"\], which gets the function to count all types of pieces. If, for example, you only want to count pawns and white rooks, you can send in \["P", "p", "R"\]. The list can also contain members of the Stockfish.Piece enum, if you'd prefer to use this custom enum of the Stockfish class. E.g., sending in \[Stockfish.Piece.WHITE_PAWN, Stockfish.Piece.BLACK_PAWN, Stockfish.Piece.WHITE_ROOK\] as the argument will yield the same behaviour.  

Some example calls to the function (let's assume the current position is the starting chess position):  
```python
stockfish.get_num_pieces(specific_rank=2) # returns 8
stockfish.get_num_pieces(specific_file="b", pieces_to_count=['N', 'p']) # returns 2, since on the b-file there is one white knight and one black pawn.
stockfish.get_num_pieces(specific_file="e") # returns 4
stockfish.get_num_pieces(specific_rank=8, pieces_to_count=[Stockfish.Piece.BLACK_PAWN]) # returns 0, since there are no black pawns on the 8th rank.
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
