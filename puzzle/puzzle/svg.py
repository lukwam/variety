# -*- coding: utf-8 -*-
"""SVG class file."""
import json
from xml.dom import minidom

from flask import render_template


class SVG:
    """SVG class."""

    def __init__(self, filename=None, string=None):
        """Initialize an SVG instance."""
        if filename:
            self.doc = minidom.parse(filename)
        elif string:
            self.doc = minidom.parseString(string)
        else:
            raise ValueError("Must provide either a filename or string")

        self.puzzle = {}

        self._parse()

    def _parse(self):
        """Parse the SVG file."""
        output = []

        rows = int(self.doc.documentElement.getAttribute("data-rows"))
        cols = int(self.doc.documentElement.getAttribute("data-cols"))

        # initialize the grid
        grid = []
        for row in range(rows):
            grid.append([])
            for col in range(cols):
                grid[row].append({"row": row, "col": col})

        # get metadata
        data_title = self.doc.documentElement.getAttribute("data-title")
        date = data_title.split(" ")[0]
        title = data_title.replace(date, "").strip()
        if len(date) == 7:
            date += "-01"
        title = title.replace(" (solution)", "")

        # add metadata to output
        output.append(f"title: {title}")
        output.append("author: Emily Cox and Henry Rathvon")
        output.append(f"date: {date}")
        output.append("publication: PUBLICATION_NAME")
        output.append("\ninstructions: |\n  REPLACE_THESE_INSTRUCTIONS.")

        # get groups
        for group in self.doc.getElementsByTagName("g"):
            gid = group.getAttribute("id")

            # get answers
            if gid == "svg-answers":
                for text in group.getElementsByTagName("text"):
                    col = int(text.getAttribute("data-col"))
                    row = int(text.getAttribute("data-row"))
                    answer = text.firstChild.nodeValue
                    grid[row][col]["answer"] = answer

            # get numbers
            if gid == "svg-numbers":
                for text in group.getElementsByTagName("text"):
                    col = int(text.getAttribute("data-col"))
                    row = int(text.getAttribute("data-row"))
                    number = text.firstChild.nodeValue
                    grid[row][col]["number"] = number

            # get across bars
            if gid == "svg-acrossbars":
                for line in group.getElementsByTagName("line"):
                    col = int(line.getAttribute("data-col"))
                    row = int(line.getAttribute("data-row"))
                    grid[row][col]["across-bar"] = True

            # get down bars
            if gid == "svg-downbars":
                for line in group.getElementsByTagName("line"):
                    col = int(line.getAttribute("data-col"))
                    row = int(line.getAttribute("data-row"))
                    grid[row][col]["down-bar"] = True

            # get shadesquares
            if gid == "svg-shadesquares":
                for rect in group.getElementsByTagName("use"):
                    col = int(rect.getAttribute("data-col"))
                    row = int(rect.getAttribute("data-row"))
                    fill = rect.getAttribute("fill")
                    if fill == "#000000":
                        grid[row][col]["block"] = True
                    else:
                        grid[row][col]["shade-square"] = fill

        # add grid to output
        output.append("\ngrid:")

        across_rows = []
        output.append("\n  rows:")
        for row in range(rows):
            line = ""
            for col in range(cols):
                if grid[row][col].get("across-bar"):
                    line += "|"
                answer = grid[row][col].get("answer")
                block = grid[row][col].get("block")
                # shade_square = grid[row][col].get("shade-square")
                if answer:
                    line += answer
                elif block:
                    line += "#"
                else:
                    line += "_"
            text = f"{line}".strip("|")
            across_rows.append(text)
            output.append(f"    - {text}")

        down_rows = []
        output.append("\n  columns:")
        for col in range(cols):
            line = ""
            for row in range(rows):
                if grid[row][col].get("down-bar"):
                    line += "|"
                answer = grid[row][col].get("answer")
                block = grid[row][col].get("block")
                # shade_square = grid[row][col].get("shade-square")
                if answer:
                    line += answer
                elif block:
                    line += "#"
                else:
                    line += "_"
            text = f"{line}".strip("|")
            down_rows.append(text)
            output.append(f"    - {text}")

        output.append("\nclues:")

        output.append("\n  Across:")
        n = 1
        across_clues = []
        for row in across_rows:
            for word in row.replace("_", "|").replace("#", "").split("|"):
                if len(word) > 1:
                    clue = f"    {n}. CLUE ~ {word} ~ SOLUTION"
                    output.append(clue)
                    across_clues.append(clue.strip())
                    n += 1

        output.append("\n  Down:")
        n = 1
        down_clues = []
        for col in down_rows:
            for word in col.replace("_", "|").replace("#", "").split("|"):
                if len(word) > 1:
                    clue = f"    {n}. CLUE ~ {word} ~ SOLUTION"
                    output.append(clue)
                    down_clues.append(clue.strip())
                    n += 1

        print("\n".join(output))

        self.puzzle = {
            "title": title,
            "date": date,
            "clues": [
                {
                    "name": "Across",
                    "clues": across_clues,
                },
                {
                    "name": "Down",
                    "clues": down_clues,
                },
            ],
            "grid": {
                "rows": across_rows,
                "columns": down_rows,
                "style": [],
                "styles": {},
            },
        }

    def create(self, puzzle):
        """Return an SVG string of the puzzle."""
        body = render_template("svg.html", puzzle=puzzle)
        return body
