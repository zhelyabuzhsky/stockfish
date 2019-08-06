# Stockfish
[![Build Status](https://travis-ci.org/zhelyabuzhsky/stockfish.svg?branch=master)](https://travis-ci.org/zhelyabuzhsky/stockfish)

Implements an easy-to-use Stockfish class to integrates the Stockfish chess engine with Python.

## Install

```bash
$ pip install stockfish
```

## Features
- set current position
- get best move

## Usage

```python
from stockfish import Stockfish

# you should install the stockfish engine in your operating system globally or specify path to binary file in class constructor
stockfish = Stockfish('/Users/zhelyabuzhsky/Work/stockfish/stockfish-9-64')

# set position by moves:
stockfish.set_position(['e2e4', 'e7e6'])

# set position by FEN:
stockfish.set_fen_position("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")

print(stockfish.get_best_move()) # d2d4
print(stockfish.is_move_correct('a2a3')) # True
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
GNU General Public License, version 3. Please see [License File](LICENSE) for more information.
