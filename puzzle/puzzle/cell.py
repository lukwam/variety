# -*- coding: utf-8 -*-
"""Cell class file."""


class Cell:
    """Cell class."""

    def __init__(self, row, col, value, grid, name=None):
        """Initialize the Cell class."""
        self._value = None

        self.col = col
        self.row = row
        self.x = col
        self.y = row

        self.name = name
        self.value = value

        # grid
        self.grid = grid

        # bars
        self._bottom_bar = False
        self._left_bar = False
        self._right_bar = False
        self._top_bar = False

        # styling information
        self._blank = False
        self._block = False
        self.default = None
        self.styles = {}

    @property
    def blank(self):
        """Return true if this cell is blank."""
        return self._blank

    @property
    def block(self):
        """Return true if this cell is a block."""
        return self._block

    @property
    def bottom_bar(self):
        """Return true if cell has a bottom bar."""
        if self._bottom_bar:
            return True
        if not self.grid.puzzle.show_grid_border:
            return False
        try:
            bottom = self.grid.grid[self.row + 1][self.col]
            if self.value and not bottom.value:
                return True
        except Exception:
            return False
        return False

    @property
    def bottom_border(self):
        """Return true if cell has a bottom border."""
        if not self.grid.puzzle.show_grid_border:
            return False
        if self.row == self.grid.height - 1 and (self.value or self.block):
            return True
        try:
            bottom = self.grid.grid[self.row + 1][self.col]
            if self.value and not bottom.value:
                return True
        except Exception:
            return False
        return False

    @property
    def left_bar(self):
        """Return true if cell has a left bar."""
        if self._left_bar:
            return True
        if not self.grid.puzzle.show_grid_border:
            return False
        if self.col > 0:
            try:
                left = self.grid.grid[self.row][self.col - 1]
                if bool(self.value) ^ bool(left.value):
                    return True
            except Exception:
                return False
        return False

    @property
    def left_border(self):
        """Return true if cell has a left border."""
        if not self.grid.puzzle.show_grid_border:
            return False
        if self.col == 0 and (self.value or self.block):
            return True
        if self.col > 0:
            try:
                left = self.grid.grid[self.row][self.col - 1]
                if self.value and not left.value:
                    return True
            except Exception:
                return False
        return False

    @property
    def right_bar(self):
        """Return true if cell has a right var."""
        if self._right_bar:
            return True
        if not self.grid.puzzle.show_grid_border:
            return False
        try:
            right = self.grid.grid[self.row][self.col + 1]
            if bool(self.value) ^ bool(right.value):
                return True
        except Exception:
            return False
        return False

    @property
    def right_border(self):
        """Return true if cell has a right border."""
        if not self.grid.puzzle.show_grid_border:
            return False
        if self.col == self.grid.width - 1 and (self.value or self.block):
            return True
        try:
            right = self.grid.grid[self.row][self.col + 1]
            if self.value and not right.value:
                return True
        except Exception:
            return False
        return False

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
    def shade_circle(self):
        """Return the background-color if cell has a shade circle."""
        shape = self.styles.get("shape")
        if shape != "circle":
            return False
        if "fill" in self.styles:
            return self.styles.get("fill")
        return False

    @property
    def shade_square(self):
        """Return the background-color if cell has a shade square."""
        if "background-color" in self.styles:
            return self.styles.get("background-color")
        return False

    @property
    def style(self):
        """Return the style of this cell."""
        if len(self.grid.style) > self.row and len(self.grid.style[self.row]) > self.col:
            style = self.grid.style[self.row][self.col]
            if style != "_":
                return style
        return None

    @property
    def top_bar(self):
        """Return true if cell has a top bar."""
        if self._top_bar:
            return True
        if not self.grid.puzzle.show_grid_border:
            return False
        if self.row > 0:
            try:
                top = self.grid.grid[self.row - 1][self.col]
                if bool(self.value) ^ bool(top.value):
                    return True
            except Exception:
                return False
        return False

    @property
    def top_border(self):
        """Return true if cell has a top border."""
        if not self.grid.puzzle.show_grid_border:
            return False
        if self.row == 0 and (self.value or self.block):
            return True
        if self.row > 0:
            try:
                top = self.grid.grid[self.row - 1][self.col]
                if self.value and not top.value:
                    return True
            except Exception:
                return False
        return False

    @property
    def value(self):
        """Return the value of this cell."""
        return self._value

    @value.setter
    def value(self, value):
        """Set the value of this cell."""
        # catch blanks
        if value == "_":
            self._blank = True
        # catch blocks
        elif value == "#":
            self._block = True
        # handle periods as spaces
        elif value == ".":
            self._value = " "
        else:
            self._value = value
