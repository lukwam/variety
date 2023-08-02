# -*- coding: utf-8 -*-
"""Cell class file."""


class Cell:
    """Cell class."""

    def __init__(self, row, col, value, grid, name=None):
        """Initialize the Cell class."""
        self.row = row
        self.col = col
        self.value = value
        self.name = name

        # grid
        self.grid = grid

        # bars
        self._bottom_bar = False
        self._left_bar = False
        self._right_bar = False
        self._top_bar = False

        # styling information
        self.default = None
        self.styles = {}

    @property
    def blank(self):
        """Return true if this cell is blank."""
        return True if self.value is None else False

    @property
    def block(self):
        """Return true if this cell is a block."""
        return True if self.value == "#" else False

    @property
    def style(self):
        """Return the style of this cell."""
        if len(self.grid.style) > self.row and len(self.grid.style[self.row]) > self.col:
            style = self.grid.style[self.row][self.col]
            if style != "_":
                return style
        return None

    def set_bottom_bar(self):
        """Set the bottom bar."""
        self._bottom_bar = True

    def set_left_bar(self):
        """Set the left bar."""
        self._left_bar = True

    def set_right_bar(self):
        """Set the right bar."""
        self._right_bar = True

    def set_top_bar(self):
        """Set the top bar."""
        self._top_bar = True

    @property
    def bottom_bar(self):
        """Return true if cell has a bottom bar."""
        if self._bottom_bar:
            return True
        try:
            bottom = self.grid.grid[self.row + 1][self.col]
            if not self.value and bottom.value and self.grid.puzzle.show_grid_border:
                return True
        except Exception:
            return False
        return False

    @property
    def bottom_border(self):
        """Return true if cell has a bottom border."""
        if self.value and self.row == self.grid.height - 1:
            return True
        return False

    @property
    def left_bar(self):
        """Return true if cell has a left bar."""
        if self._left_bar:
            return True
        if self.col > 0:
            try:
                left = self.grid.grid[self.row][self.col - 1]
                if not self.value and left.value and self.grid.puzzle.show_grid_border:
                    return True
            except Exception:
                return False
        return False

    @property
    def left_border(self):
        """Return true if cell has a left border."""
        if self.value and self.col == 0:
            return True
        return False

    @property
    def right_bar(self):
        """Return true if cell has a right var."""
        if self._right_bar:
            return True
        try:
            right = self.grid.grid[self.row][self.col + 1]
            if not self.value and right.value and self.grid.puzzle.show_grid_border:
                return True
        except Exception:
            return False
        return False

    @property
    def right_border(self):
        """Return true if cell has a right border."""
        if self.value and self.col == self.grid.width - 1:
            return True
        return False

    @property
    def top_bar(self):
        """Return true if cell has a top bar."""
        if self._top_bar:
            return True
        if self.row > 0:
            try:
                top = self.grid.grid[self.row - 1][self.col]
                if not self.value and top.value and self.grid.puzzle.show_grid_border:
                    return True
            except Exception:
                return False
        return False

    @property
    def top_border(self):
        """Return true if cell has a top border."""
        if self.value and self.row == 0:
            return True
        return False
