# -*- coding: utf-8 -*-
"""Support for the Hex format for cryptic crosswords."""
from cryptic.core import CrosswordCell
from cryptic.core import CrypticClues
from cryptic.core import CrypticCluesContainer
from cryptic.core import CrypticCrossword


def from_hex(hex_dict):
    """Return a Crossword object from a hex dict."""
    known_keys = [
        "metadata",
        "instructions",
        "solution",
        "grid",
        "clues",
        "settings",
        "unclued",
        "width",
        "height",
        "words",
    ]

    width = hex_dict.get("width")
    height = hex_dict.get("height")
    crossword = CrypticCrossword(width, height)

    crossword._format_identifier = CrypticCrossword.HEX
    crossword.meta.contributor = hex_dict["metadata"].get('editor')
    crossword.meta.creator = hex_dict["metadata"].get('author')
    crossword.meta.date = hex_dict["metadata"].get('date')
    crossword.meta.description = hex_dict.get('instructions')
    crossword.meta.identifier = hex_dict["metadata"].get('number')
    crossword.meta.publisher = hex_dict["metadata"].get('publication')
    crossword.meta.rights = hex_dict["metadata"].get('copyright')
    crossword.meta.source = hex_dict["metadata"].get('issue')
    crossword.meta.title = hex_dict["metadata"].get('title')
    crossword.block = hex_dict["settings"].get('block')
    crossword.empty = hex_dict["settings"].get('empty')

    crossword.solution = hex_dict.get('solution')
    crossword.words = hex_dict.get('words', {})

    # create clue containers and clues
    clues = hex_dict.get("clues", {})
    crossword.clues = CrypticClues()
    for title, clue_list in clues.items():
        crossword.clues[title] = CrypticCluesContainer()
        for clue in clue_list:
            name = clue.get("name")
            crossword.clues[title][name] = clue

    # create empty grid of cells
    for x, y in crossword.cells:
        crossword[x, y] = CrosswordCell()

    # fill in the answers, bars and blocks
    grid = hex_dict.get("grid", {})
    for index, cell in grid.items():
        x, y = index
        if cell.get("block"):
            crossword[x, y].block = True
        if cell.get("empty"):
            crossword[x, y].empty = True
        if cell.get("entry"):
            crossword[x, y].entry = cell["entry"]
        if cell.get("number"):
            crossword[x, y].number = cell["number"]
        if cell.get("bottom_bar"):
            crossword[x, y].bottom_bar = True
        if cell.get("right_bar"):
            crossword[x, y].right_bar = True

    # add unknown keys to format-specific data dict
    for key, value in hex_dict.items():
        if key not in known_keys:
            crossword._format[key] = value

    return crossword


def to_hex(crossword):
    """Return a hex dict from a Crossword object."""
    raise NotImplementedError
