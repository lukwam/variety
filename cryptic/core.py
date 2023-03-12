# -*- coding: utf-8 -*-
"""Classes for working with cryptic crosswords."""
import collections
import os

from crossword import Crossword
from crossword.core import CrosswordCell
from crossword.core import CrosswordDirectionClues as CrypticCluesContainer
from crossword.core import CrosswordMetadata


class CrypticClues(collections.OrderedDict):
    """An object that contains the clues for a cryptic crossword."""

    def __init__(self, *args, **kwargs):
        """Initialize a new crossword puzzle clues object."""
        super(CrypticClues, self).__init__(*args, **kwargs)
        # TODO: Decide how to initialize a new clues object.

    def __getattr__(self, name):
        """Access dict items as attributes."""
        try:
            return self[name]
        except KeyError:
            raise AttributeError

    def all(self, sort=int):
        """Return a generator of all clues."""
        for title in self:
            for number, clue in self[title](sort=sort):
                yield title, number, clue


class CrypticCrossword(Crossword):
    """A cryptic crossword puzzle."""

    HEX = "hex"

    def __init__(self, width=15, height=15):
        """Initialize a new crossword puzzle object."""
        if width <= 0:
            raise ValueError("Width needs to be at least one")
        if height <= 0:
            raise ValueError("Height needs to be at least one")

        # set the dimensions of the grid
        self.width = width
        self.height = height

        # create a two-dimensional array of crossword cells
        self._data = [
            [CrosswordCell() for _ in range(width)] for _ in range(height)
        ]

        # create the metadata and clues objects
        self.meta = CrosswordMetadata()
        self.clues = CrypticClues()

        # file format-specific identifier and data
        self._format_identifier = None
        self._format = {}

        # override the default block ("#") and empty ("_") characters
        self.block = None
        self.empty = None

        # add an attribute for solution
        self.solution = None

    @property
    def content(self):
        """Return a dict with the content of the puzzle."""
        return {
            'width': self.width,
            'height': self.height,
            'cells': self._data,
            'metadata': self.meta,
            'clues': {title: self.clues[title] for title in self.clues},
            'block': self.block,
            'empty': self.empty,
            'type': self._format_identifier,
            'format': self._format,
        }

    def __str__(self):
        """Return the string representation of a puzzle."""
        result = []
        for row in self:
            for cell in row:
                if cell.get("block"):
                    value = "#"
                if cell.get("empty"):
                    value = "_"
                if cell.get("entry"):
                    value = cell.get("entry")
                if not value:
                    value = "_"
                result.append(value)
            result.append(str(os.linesep))
        return str('').join(result)
