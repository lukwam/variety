# -*- coding: utf-8 -*-
"""Hex class file."""
import logging

import yaml

BAR = "|"

BLOCK = "#"

EMPTY = "_"

KEYS = [
    "title",         # title of the puzzle
    "author",        # author of the puzzle
    "editor",        # editor of the puzzle
    "date",          # date the puzzle was published
    "publication",   # publication the puzzle was published in
    "issue",         # issue of the publication the puzzle was published in
    "number",        # number of the puzzle in the publication
    "instructions",  # instructions for solving the puzzle
    "solution",      # solution to the puzzle
    # grid data {rows: [row, ...], columns: [column, ...], (style: [style, ...], styles: {style: {key: value, ...}, ...})}
    "grid",
    # clues data: [{title: [{number, clue, answers, explanations}, ...]}, ...]
    "clues",
    "settings",      # settings data: {key: value, ...}
    "unclued",       # unclued entries: [entry, ...]
]


def _get_across_words(rows):
    """Return a dict of across words."""
    words = {}
    for y, row in enumerate(rows):
        ltrs = row.replace(BAR, "").replace(BLOCK, "").replace(EMPTY, "")
        for word in row.replace(BLOCK, BAR).replace(EMPTY, BAR).split(BAR):
            if len(word) > 1:
                x1 = ltrs.index(word)
                x2 = ltrs.index(word) + len(word) - 1
                y1 = y
                y2 = y
                words[word] = {
                    "direction": "across",
                    "x1": x1, "x2": x2, "y1": y1, "y2": y2,
                }
    return words


def _get_down_words(columns):
    """Return a dict of across words."""
    words = {}
    for x, col in enumerate(columns):
        ltrs = col.replace(BAR, "").replace(BLOCK, "").replace(EMPTY, "")
        for word in col.replace(BLOCK, BAR).replace(EMPTY, BAR).split(BAR):
            if len(word) > 1:
                y1 = ltrs.index(word)
                y2 = ltrs.index(word) + len(word) - 1
                x1 = x
                x2 = x
                words[word] = {
                    "direction": "down",
                    "x1": x1, "x2": x2, "y1": y1, "y2": y2,
                }
    return words


def _parse_clue(item):
    """Parse a clue."""
    name, rest = item.split(" ", 1)
    name = name.strip(".")

    # allow clues to be grouped (e.g. "1|a", "1|b", 1|c", ...)
    heading = None
    subheading = None
    if "|" in name:
        heading, subheading = name.split("|", 1)
        name = name.replace("|", "")

    # get the clue, answer and explanation
    clue, answer, explanation = rest.split(" ~ ")

    # get entry
    entry = ""
    if "|" in answer:
        answer, entry = answer.split("|", 1)

    # allow for multiple answers, entries and explanations
    answers = answer.split(";") if answer else []
    entries = entry.split(";") if entry else []
    explanations = explanation.split(";")

    if not entries:
        for answer in answers:
            entries.append(answer.replace(" ", "").replace("-", ""))

    return {
        "name": name,
        "heading": heading,
        "subheading": subheading,
        "clue": clue,
        "answers": answers,
        "answer_enums": [],
        "entries": entries,
        "entry_enums": [],
        "explanations": explanations,
    }


def _parse_clues(data, grid, words):
    """Parse the clues."""
    clues = {}

    for title, container in data.items():
        clues[title] = []

        options = []
        if " ~ " in title:
            options = title.split(" ~ ")[1].split(",")

        # parse the clues from a string
        if isinstance(container, str):
            items = container.strip().split("\n")
            for item in items:
                clue = _parse_clue(item)

                # identify and label grid words with clue info
                name = clue["name"]
                entries = clue["entries"]
                for entry in entries:
                    if entry in words:
                        words[entry]["clue"] = name
                        words[entry]["clue_container"] = title
                        # number the grid entry
                        x = words[entry]["x1"]
                        y = words[entry]["y1"]
                        cell = grid[x, y]
                        number = cell.get("number")
                        if number and number != name:
                            print(
                                f"WARNING: {x}, {y} already numbered {number} ({name})",
                            )
                            continue
                        cell["number"] = name
                    else:
                        print(f"WARNING: {entry} not found in grid words")

                clues[title].append(clue)

    return clues


def _parse_grid(data, block=BLOCK, empty=EMPTY):
    """Parse the grid."""
    columns = data.get("columns", [])
    rows = data.get("rows", [])

    style = data.get("style", [])
    styles = data.get("styles", {})

    width = len(columns)
    height = len(rows)

    # initialize the grid
    grid = {}
    for y in range(height):
        for x in range(width):
            index = x, y
            grid[index] = {"index": index}

    _parse_grid_columns(columns, grid)
    _parse_grid_rows(rows, grid)

    # parse the style information
    for y, row in enumerate(style):
        for x, char in enumerate(row):
            char = char.strip()
            if not char:
                continue
            if "style" not in grid[x, y]:
                grid[x, y]["style"] = {}
            grid[x, y]["style"][char] = styles.get(char, {})

    # get words from the grid
    across_words = _get_across_words(rows)
    down_words = _get_down_words(columns)
    words = {**across_words, **down_words}

    return width, height, grid, words


def _parse_grid_columns(columns, grid):
    """Parse the grid columns."""
    x = 0
    for column in columns:
        y = 0
        for char in column:
            if char == BAR:
                if 0 < y:
                    grid[(x, y - 1)]["bottom_bar"] = True
                continue
            if char == BLOCK:
                grid[x, y]["block"] = True
                y += 1
                continue
            if char == EMPTY:
                grid[x, y]["empty"] = True
                y += 1
                continue
            grid[x, y]["entry"] = char
            y += 1
        x += 1


def _parse_grid_rows(rows, grid):
    """Parse the grid rows."""
    y = 0
    for row in rows:
        x = 0
        for char in row:
            if char == BAR:
                if 0 < x:
                    grid[(x - 1, y)]["right_bar"] = True
                continue
            if char == BLOCK:
                grid[x, y]["block"] = True
                x += 1
                continue
            if char == EMPTY:
                grid[x, y]["empty"] = True
                x += 1
                continue
            if (x, y) in grid:
                grid[x, y]["entry"] = char
            else:
                logging.warning(f"Missing entry: {x}, {y}: {char}")
            x += 1
        y += 1


def read(filename):
    """Read a .hex file and return a dict."""
    with open(filename) as f:
        return load(yaml.safe_load(f))


def load(data):
    """Read .hex file data and return a dict."""
    puzzle = {
        "metadata": {
            "title": data.get("title"),
            "author": data.get("author"),
            "editor": data.get("editor"),
            "date": data.get("date"),
            "publication": data.get("publication"),
            "issue": data.get("issue"),
            "number": data.get("number"),
        },
        "instructions": data.get("instructions"),
        "solution": data.get("solution"),
        "grid": {},
        "clues": {},
        "settings": data.get("settings", {}),
        "unclued": data.get("unclued", []),
    }

    block = puzzle["settings"].get("block", BLOCK)
    empty = puzzle["settings"].get("empty", EMPTY)

    # parse grid
    grid_data = data.get("grid", {})
    width, height, grid, words, = _parse_grid(grid_data, block, empty)
    puzzle["width"] = width
    puzzle["height"] = height
    puzzle["grid"] = grid
    puzzle["words"] = words

    # parse clues
    clues_data = data.get("clues", {})
    clues = _parse_clues(clues_data, grid, words)
    puzzle["clues"] = clues

    return puzzle
