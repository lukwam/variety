# -*- coding: utf-8 -*-
"""Variety is a Python library for working with cryptic crosswords."""
import os

from cryptic import from_hex
from hex import read as read_hex


def main():
    """Main function."""
    # filename = "puzzles/wsj020.yaml"
    # filenames = [filename]

    skip = [
        "puzzles/atl005.yaml",
    ]

    filenames = []
    for file in os.listdir("puzzles"):
        if file.endswith(".yaml"):
            filenames.append(os.path.join("puzzles", file))

    for filename in sorted(filenames):
        if filename in skip:
            continue
        print(f"# {filename}")
        hex_dict = read_hex(filename)
        puzzle = from_hex(hex_dict)
        print(puzzle)


if __name__ == "__main__":
    main()
