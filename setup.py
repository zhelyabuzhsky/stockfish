from setuptools import find_packages, setup

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="stockfish",
    author="Ilya Zhelyabuzhsky",
    author_email="zhelyabuzhsky@icloud.com",
    version="3.13.0",
    license="MIT",
    keywords="chess stockfish",
    python_requires=">=3.6",
    url="https://github.com/zhelyabuzhsky/stockfish",
    description="Wraps the open-source Stockfish chess engine for easy integration into python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=["stockfish", "stockfish.*"]),
    install_requires=[],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    classifiers=[
        "Programming Language :: Python",
        "Natural Language :: English",
        "Operating System :: Unix",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
