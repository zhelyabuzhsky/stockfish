from setuptools import setup

setup(
    name="stockfish",
    author='Ilya Zhelyabuzhsky',
    author_email="zhelyabuzhsky@gmail.com",
    version="1.0.2",
    license="GPLv3",
    keywords="chess stockfish",
    url='https://github.com/zhelyabuzhsky/stockfish',
    py_modules=["stockfish"],
    description="Wraps the open-source Stockfish chess engine for easy integration into python.",
    long_description='''
    This integrates the Stockfish chess engine with python. It allows the engine to be used
    by invoking an easy-to-use Engine class with synchronization handled automatically.
    ''',
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: Unix",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ])
