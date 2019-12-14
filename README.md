# Stockfish
Implements an easy-to-use Stockfish class to integrates the Stockfish chess engine with Python.

## Install
```bash
$ pip install stockfish
```

#### Ubuntu or Debian
```bash
# apt install stockfish
``` 

#### Mac OS
```bash
$ brew install stockfish
```

## Features
- set current position
- get best move
- change engine's skill level
- get current engine's parameters

## Usage

```python
from stockfish import Stockfish

# you should install the stockfish engine in your operating system globally or specify path to binary file in class constructor
stockfish = Stockfish('/Users/zhelyabuzhsky/Work/stockfish/stockfish-9-64')

# set position by sequence of moves:
stockfish.set_position(['e2e4', 'e7e6'])

# set position by Forsyth–Edwards Notation (FEN):
stockfish.set_fen_position("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")

print(stockfish.get_best_move()) # d2d4
print(stockfish.is_move_correct('a2a3')) # True

# get last move info:
print(stockfish.info)
# e.g. 'info depth 2 seldepth 3 multipv 1 score mate -1 nodes 11 nps 5500 tbhits 0 time 2 pv h2g1 h4g3'

# set current engine's skill level:
stockfish.set_skill_level(15)

# get current engine's parameters:
stockfish.get_parameters()
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
