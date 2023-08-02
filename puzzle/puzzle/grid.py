# -*- coding: utf-8 -*-
"""Grid class file."""
import json
import logging
import re

from puzzle.cell import Cell


class Grid:
    """Grid class."""

    def __init__(self, puzzle):
        """Initialize the Grid class."""
        self.puzzle = puzzle

        # get the grid data (rows and columns)
        self.grid = self.puzzle.puzzle.get("grid", {})
        self.columns = self.grid["columns"]
        self.rows = self.grid["rows"]

        # get the grid metadata (style and styles)
        self.style = self.grid.get("style", [])
        self.styles = self.grid.get("styles", {})

        # create empty grid
        self.grid = []
        for _ in range(self.height):
            self.grid.append([None] * self.width)

        self.create_grid()

    @property
    def entries(self):
        """Return the entries from the grid."""
        across_entries = self._across_entries()
        down_entries = self._down_entries()
        entries = across_entries + down_entries
        return entries

    @property
    def height(self):
        """Return the height."""
        # height = len(self.rows)
        # for col in self.columns:
        #     if col and len(col) > height:
        #         height = len(col)
        # return height
        return len(self.rows)

    @property
    def width(self):
        """Return the width."""
        # width = len(self.columns)
        # for row in self.rows:
        #     if len(row) > width:
        #         width = len(row)
        # return width
        return len(self.columns)

    def _across_entries(self):
        """Return the across entries."""
        return self._parse_entries(self.rows)

    def _down_entries(self):
        """Return the down entries."""
        return self._parse_entries(self.columns)

    def _parse_entries(self, items):
        """Parse the entries."""
        entries = []
        for item in items:
            for word in re.sub("[_#]", "|", item).split("|"):
                if len(word) > 1:
                    entries.append(word)
        return entries

    def create_cell(self, row, col, value, name=None):
        """Create a cell."""
        if value == "_":
            value = None
        cell = Cell(row, col, value, self, name)
        try:
            self.grid[row][col] = cell
        except IndexError:
            error = f"Index error at {row}-{col}: {value}"
            logging.error(error)
        return cell

    def create_grid(self):
        """Creat the grid data."""
        self.create_grid_rows()
        self.create_grid_columns()
        self.parse_grid_style()

    def create_grid_columns(self):
        """Create the grid columns."""
        # for each column in the list of all columns
        for col, entries in enumerate(self.columns):
            row = 0
            # get the list of words for this column
            words = entries.rstrip("_").split("|")
            # for each word in this column
            for word in words:
                # initialize a cell
                cell = None
                # for each character in this word
                for n, char in enumerate(word):
                    # name of the cell starts out as None
                    name = None
                    # check if this word gets a name (label)
                    if len(word) > 1 and n == 0:
                        if word in self.puzzle.entries:
                            clue = self.puzzle.entries[word]
                            if clue.show_grid_label:
                                name = clue.label
                    # check if this cell already exists
                    if len(self.grid) > row and len(self.grid[row]) > col and self.grid[row][col]:
                        cell = self.grid[row][col]
                        # check if the name is already set, or set it
                        if name:
                            if cell.name:
                                if cell.name != name:
                                    logging.warning(
                                        f"Cell {row}, {col} already as a label: {cell.name}",
                                    )
                            else:
                                cell.name = name
                        # check if the value is already set and doesn't match
                        if cell.value and cell.value != char:
                            error = (
                                f"Value mismatch parsing columns at {row}-{col}:"
                                f" {char} != {cell.value}"
                            )
                            logging.error(error)
                            cell.value = char + "/" + cell.value
                    # if the cell doesn't already exist, create it
                    else:
                        cell = self.create_cell(row, col, char, name)
                        while len(self.grid) < row + 1:
                            self.grid.append([])
                        while len(self.grid[row]) < col + 1:
                            self.grid[row].append([])
                        self.grid[row][col] = cell
                    # check if the cell needs a top bar added to it
                    if n == 0 and cell.value:
                        cell.set_top_bar()
                    # check if the cell needs a bottom bar added to it
                    if n == len(word) - 1 and cell.value:
                        cell.set_bottom_bar()
                    row += 1
            # add additional cells to fill out the rectangle
            while row < self.height:
                cell = self.create_cell(row, col, "_", None)
                row += 1

    def create_grid_rows(self):
        """Create the grid rows."""
        # for each row in the list of all rows
        for row, entries in enumerate(self.rows):
            col = 0
            # get the list of words for this row (remove unused cells at tend of the row)
            words = entries.rstrip("_").split("|")
            # for each word in this row
            for word in words:
                # initialize a cell
                cell = None
                # for each character in this word
                for n, char in enumerate(word):
                    # name of the cell starts out as None
                    name = None
                    # check if this word gets a name (label)
                    if len(word) > 1 and n == 0:
                        if word in self.puzzle.entries:
                            clue = self.puzzle.entries[word]
                            if clue.show_grid_label:
                                name = clue.label
                    # check if this cell already exists
                    if len(self.grid) > row and len(self.grid[row]) > col and self.grid[row][col]:
                        cell = self.grid[row][col]
                        # check if the name is already set, or set it
                        if name:
                            if cell.name:
                                if cell.name != name:
                                    logging.warning(
                                        f"Cell {row}, {col} already as a label: {cell.name}",
                                    )
                            else:
                                cell.name = name
                        # check if the value is already set and doesn't match
                        if cell.value and cell.value != char:
                            error = (
                                f"Value mismatch parsing rows at {row}-{col}:"
                                f" {char} != {cell.value}"
                            )
                            logging.error(error)
                            cell.value += "/" + char
                    # if the cell doesn't already exist, create it
                    else:
                        cell = self.create_cell(row, col, char, name)
                        while len(self.grid) < row + 1:
                            self.grid.append([])
                        while len(self.grid[row]) < col + 1:
                            self.grid[row].append([])
                        self.grid[row][col] = cell
                    # check if the cell needs a left bar added to it
                    if n == 0 and cell.value:
                        cell.set_left_bar()
                    # check if the cell needs a right bar added to it
                    if n == len(word) - 1 and cell.value:
                        cell.set_right_bar()
                    col += 1
            # add additional cells to fill out the rectangle
            while col < self.width:
                cell = self.create_cell(row, col, "_", None)
                col += 1

    def display_grid(self, show_answers=False, show_numbers=True):
        """Display the grid."""
        border = " " + "-" * (self.width * 4 - 1) + " \n"

        output = "\n"
        output += border

        for row_index, row in enumerate(self.grid):

            # display across entries and bars
            row_output = "|"
            for col_index, cell in enumerate(row):
                value = "   "
                if show_answers and cell and cell.value:
                    value = cell.value.center(3)
                elif show_numbers and cell and cell.name:
                    value = str(cell.name).ljust(3)
                elif len(self.style) > row_index:
                    style = self.style[row_index]
                    value = style[col_index].center(3)
                row_output += value
                if cell and cell.right_bar:
                    row_output += "|"
                else:
                    row_output += " "
            output += row_output + "\n"

            # display down bars
            row_output = "|"
            for col_index, cell in enumerate(row):
                if cell and cell.bottom_bar:
                    row_output += "---"
                else:
                    row_output += "   "
                if col_index < self.width - 1:
                    row_output += " "

            # skip last row
            if row_index < self.height - 1:
                output += row_output + "|\n"

        output += border
        print(output)

    def parse_grid_style(self):
        """Parse the style information for the grid and update the cells accordingly."""
        print("Parsing grid styles...")
        # print("\n".join(self.style))
        print(json.dumps(self.styles, indent=2, sort_keys=True))

        for y, row in enumerate(self.style):
            values = {}

            # remove multi-character values from the string, which are literals
            matches = re.findall(r"\[(.*?)\]", row)
            for match in matches:
                text = f"[{match}]"
                x = row.find(text)
                id = (x, y)
                values[id] = match
                row = row.replace(text, " ")

            # go through the remaining characters
            for x, char in enumerate(row):
                id = (x, y)
                if id in values:
                    if char != " ":
                        print(f"ERROR: duplicate cell at {id}")
                    continue
                values[id] = char

            # update cells
            for id in sorted(values):
                value = values[id]
                x, y = id
                try:
                    cell = self.grid[y][x]
                except IndexError:
                    print(f"ERROR: cell {id} not found")
                    continue

                # check if this value has styles defined
                if value in self.styles:
                    cell_styles = self.styles[value]
                    # check if the styles define a default value
                    if "default" in cell_styles:
                        value = cell_styles["default"]
                        del cell_styles["default"]
                    if cell.styles:
                        cell.styles = cell_styles

                if value != "_":
                    cell.default = value

    def to_dict(self):
        """Return the grid as a dictionary."""
        grid = {
            "rows": self.rows,
            "columns": self.columns,
        }
        if self.style:
            grid["style"] = self.style
        if self.styles:
            grid["styles"] = self.styles
        return grid
