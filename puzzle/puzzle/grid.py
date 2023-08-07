# -*- coding: utf-8 -*-
"""Grid class file."""
# import json
import logging
import re

from puzzle.cell import Cell


class Grid:
    """Grid class."""

    default_styles = {
        "#": {
            "background-color": "lightgrey",
            "shape": "shadesquare",
        },
        "@": {
            "background-color": "lightgrey",
            "fill": "lightgrey",
            "shape": "circle",
        },
        "O": {
            "shape": "circle",
        },
        "X": {
            "shape": "x",
        },
    }

    def __init__(self, puzzle):
        """Initialize the Grid class."""
        self.puzzle = puzzle

        # get the grid data (rows and columns)
        grid = self.puzzle.puzzle.get("grid", {})
        self.columns = grid["columns"]
        self.rows = grid["rows"]
        self.style = grid.get("style", [])

        # get the solution grid data (rows and columns)
        self.solution_columns = grid.get("solution_columns", [])
        self.solution_rows = grid.get("solution_rows", [])
        self.solution_style = grid.get("solution_style", [])
        # print("\n".join(self.solution_columns))
        # print("\n".join(self.solution_rows))
        # print("\n".join(self.solution_style))

        # parse/clean the grid data
        self._parse_grid()
        # print("\n".join(self.solution_style))

        # get the grid metadata (style and styles)

        self._styles = grid.get("styles", {})

        # create empty grid
        self.grid = []
        for _ in range(self.height):
            self.grid.append([None] * self.width)

        self.solution = []
        for _ in range(self.height):
            self.solution.append([None] * self.width)

        self.create_grid()
        # self.create_grid(solution=True)

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
        return len(self.rows)

    def get_style(self, name):
        """Return the given style definition."""
        if name in self.styles:
            return self.styles[name]
        return self.default_styles.get(name)

    @property
    def styles(self):
        """Return the styles."""
        return self._styles

    @property
    def width(self):
        """Return the width."""
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
            for word in re.sub(r"[\._#]", "|", item).split("|"):
                if len(word) > 1:
                    entries.append(word)
        return entries

    def _parse_grid(self, solution=False):
        """Parse the grid data."""
        columns = self.columns
        rows = self.rows

        if solution:
            columns = self.solution_columns
            rows = self.solution_rows

        for direction in ["rows", "columns"]:
            data = columns if direction == "columns" else rows
            length = self.height if direction == "columns" else self.width

            # clean up the data
            for y, line in enumerate(data):
                line = line.strip()
                newline = ""
                for x, char in enumerate(line):
                    # check bars
                    if char == "|":
                        # skip any bars at beginning or end of line
                        if x in [0, len(line) - 1]:
                            continue
                        # skip any bars preceded or followed by an underscore
                        elif "_" in [line[x - 1], line[x + 1]]:
                            continue
                        # keep the rest of the bars
                        newline += "|"
                    else:
                        newline += char
                while len(newline) < length:
                    newline += "_"
                data[y] = newline

            if solution:
                if direction == "rows":
                    self.solution_rows = data
                else:
                    self.solution_columns = data
            else:
                if direction == "rows":
                    self.rows = data
                else:
                    self.columns = data

    def _parse_grid_entries(self, solution=False):
        """Parse the grid entries, match to clues, add labels."""
        # columns = self.columns
        # rows = self.rows
        # grid = self.grid

        # if solution:
        #     columns = self.solution_columns
        #     rows = self.solution_rows
        #     grid = self.solution

        # add labels to the across clues
        for y, row in enumerate(self.rows):
            for word in self._parse_entries([row]):
                if word in self.puzzle.entries:
                    clue = self.puzzle.entries[word]
                    x = row.replace("|", "").find(word)
                    if clue.reverse_grid_entries:
                        x += len(word) - 1
                    cell = self.grid[y][x]
                    if not clue.show_grid_label:
                        continue
                    if cell.name and cell.name != clue.label:
                        self.puzzle.error(
                            f"Duplicate cell label at {x}, {y}: {cell.name} != {clue.label}", "cell_label",
                        )
                    cell.name = clue.label
        # add labels to the down clues
        for x, column in enumerate(self.columns):
            for word in self._parse_entries([column]):
                if word in self.puzzle.entries:
                    clue = self.puzzle.entries[word]
                    y = column.replace("|", "").find(word)
                    if clue.reverse_grid_entries:
                        y += len(word) - 1
                    cell = self.grid[y][x]
                    if not clue.show_grid_label:
                        continue
                    if cell.name and cell.name != clue.label:
                        self.puzzle.error(
                            f"Duplicate cell label at {x}, {y}: {cell.name} != {clue.label}", "cell_label",
                        )
                    cell.name = clue.label

    def _pad_grid_style(self, solution=False):
        """Pad the grid style with spaces to match the dimensions of the grid."""
        style = self.style
        # if solution:
        #     style = self.solution_style
        #     print("\n".join(self.solution_style))
        # if not style:
        #     return
        while len(style) < self.height:
            style.append("_" * self.width)
        for n, row in enumerate(style):
            row += "_" * (self.width - len(row))
            style[n] = row

    def _parse_grid_style(self, solution=False):
        """Parse the style information for the grid and update the cells accordingly."""
        # grid = self.grid
        style = self.style
        # if solution:
        #     grid = self.solution
        #     style = self.solution_style

        for y, row in enumerate(style):
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
                        self.puzzle.error(
                            f"Duplicate cell at {id}", "grid_style",
                        )
                    continue
                values[id] = char

            # update cells
            for id in sorted(values):
                value = values[id]
                x, y = id
                try:
                    cell = self.grid[y][x]
                except IndexError:
                    self.puzzle.error(
                        f"Cell {id} not found: {value}", "grid_style",
                    )
                    continue

                # check if this value has styles defined
                cell_styles = self.get_style(value)
                if cell_styles:
                    # check if the styles define a default value
                    if "default" in cell_styles:
                        cell.default = cell_styles["default"]
                        del cell_styles["default"]
                    if cell_styles:
                        if cell.styles and cell.styles != cell_styles:
                            logging.warning(
                                f"Mismatched styles for {x}, {y}: {cell_styles} != {cell.styles}",
                            )
                        cell.styles = cell_styles
                elif value != "_":
                    cell.default = value

    def create_cell(self, row, col, value, name=None, solution=False):
        """Create a cell."""
        cell = Cell(row, col, value, self, name)
        # grid = self.grid
        # if solution:
        #     grid = self.solution
        try:
            self.grid[row][col] = cell
        except IndexError:
            error = f"Index error at {row}-{col}: {value}"
            logging.error(error)
        return cell

    def create_grid(self, solution=False):
        """Creat the grid data."""
        # columns = self.columns
        # rows = self.rows
        # grid = self.grid

        # if solution:
        #     columns = self.solution_columns
        #     rows = self.solution_rows
        #     grid = self.solution

        for direction in ["rows", "columns"]:
            data = self.columns if direction == "columns" else self.rows

            for b, line in enumerate(data):
                a = 0

                # create the cells
                for n, char in enumerate(line):
                    x, y = (a, b) if direction == "rows" else (b, a)

                    # skip bars as they don't create cells
                    if char == "|":
                        continue

                    # create or retreive/update the cell
                    try:
                        cell = self.grid[y][x]
                    except Exception as error:
                        logging.error(f"Failed to retrieve cell: {x}, {y}")
                        continue
                    if cell is None:
                        cell = self.create_cell(y, x, char, solution=solution)
                        if solution:
                            print(cell)
                    else:
                        if cell.value not in [None, " ", char]:
                            self.puzzle.error(
                                f"Cell value mismatch at: {x}, {y}: {char}, {cell.value}", "cell_value",
                            )
                            cell.value += f" {char}"
                        else:
                            cell.value = char

                    # check if previous character is a bar
                    if n != 0 and line[n - 1] == "|":
                        cell.set_left_bar() if direction == "rows" else cell.set_top_bar()

                    # check if next character is a bar
                    if n != len(line) - 1 and line[n + 1] == "|":
                        cell.set_right_bar() if direction == "rows" else cell.set_bottom_bar()

                    a += 1

            # parse grid
            self._parse_grid_entries(solution=solution)
            self._pad_grid_style(solution=solution)
            self._parse_grid_style(solution=solution)

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
