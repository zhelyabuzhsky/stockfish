# pystockfish
[![Build Status](https://travis-ci.org/zhelyabuzhsky/pystockfish.svg?branch=master)](https://travis-ci.org/zhelyabuzhsky/pystockfish)

Implements an easy-to-use Stockfish class to integrates the Stockfish chess engine with Python.

## Features
- set current position
- get best move

## Usage

```python
stockfish = Stockfish()
stockfish.set_position(['e2e4', 'e7e6'])
print(stockfish.get_best_move())
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
