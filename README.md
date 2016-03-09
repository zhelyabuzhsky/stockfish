# Stockfish
[![Build Status](https://travis-ci.org/zhelyabuzhsky/stockfish.svg?branch=master)](https://travis-ci.org/zhelyabuzhsky/stockfish) [![PyPI Version](https://img.shields.io/pypi/v/stockfish.svg)](https://pypi.python.org/pypi/stockfish) [![PyPI Month Downloads](https://img.shields.io/pypi/dm/stockfish.svg)](https://pypi.python.org/pypi/stockfish)

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

stockfish = Stockfish()
stockfish.set_position(['e2e4', 'e7e6'])
print(stockfish.get_best_move())
print(stockfish.is_move_correct('a2a3'))
```

## Testing

```bash
$ python test_stockfish.py
```

## Security
If you discover any security related issues, please email zhelyabuzhsky@gmail.com instead of using the issue tracker.

## Credits
- [Ilya Zhelyabuzhsky](https://github.com/zhelyabuzhsky)
- [All Contributors](../../contributors)

## License
GNU General Public License, version 3. Please see [License File](LICENSE) for more information.
