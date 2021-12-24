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

stockfish = Stockfish("/Users/zhelyabuzhsky/Work/stockfish/stockfish-9-64")
```

There are some default engine's settings:
```python
{
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
```

You can change them during your Stockfish class initialization:
```python
stockfish = Stockfish(parameters={"Threads": 2, "Minimum Thinking Time": 30})
```

### Set position by sequence of moves:
```python
stockfish.set_position(["e2e4", "e7e6"])
```

### Update position by making a sequence of moves from the current position:
```python
stockfish.make_moves_from_current_position(["g4d7", "a8b8", "f1d1"])
```

### Set position by Forsyth–Edwards Notation (FEN):
```python
stockfish.set_fen_position("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
```

### Get best move
```python
stockfish.get_best_move()
```
```text
d2d4
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

### Set current engine's skill level (ignoring ELO rating):
```python
stockfish.set_skill_level(15)
```

### Set current engine's ELO rating (ignoring skill level):
```python
stockfish.set_elo_rating(1350)
```

### Set current engine's depth:
```python
stockfish.set_depth(15)
```

### Get current engine's parameters:
```python
stockfish.get_parameters()
```
```text
{
    'Write Debug Log': 'false',
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
```

### Get current board position in Forsyth–Edwards notation (FEN):
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
```python 
stockfish.benchmark()
```
This will run the bench command with default settings. kwargs can be supplied as options.
```text
ttSize: int -> Transposition Table size in MB (max 2048)
threads: int -> Number of search threads that should be used (max 512)
limit: int -> Limit value of limitType spent for each position (max 10000)
fenFile: str -> Path to a FEN format file containing positions to bench (path/to/file.fen)
limitType: str -> Type of the limit used with limit value (depth, perft, nodes, movetime)
evalType: str -> Evaluation type used (mixed, classical, NNUE)
```

### Get current major version of stockfish engine
```python 
stockfish.get_stockfish_major_version()
```
```text
11
```

## Testing
```bash
$ python setup.py test
```

## Security
If you discover any security related issues, please email zhelyabuzhsky@icloud.com instead of using the issue tracker.

## Credits
- [Ilya Zhelyabuzhsky](https://github.com/zhelyabuzhsky)
- [All Contributors](../../contributors)

## License
MIT License. Please see [License File](LICENSE) for more information.
