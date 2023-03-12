# -*- coding: utf-8 -*-
"""Hex class file."""
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
    answers = answer.split(";")
    entries = entry.split(";")
    explanations = explanation.split(";")

    return {
        "name": name,
        "heading": heading,
        "subheading": subheading,
        "clue": clue,
        "answers": answers,
        "entries": entries,
        "explanations": explanations,
    }


def _parse_clues(data):
    """Parse the clues."""
    clues = {}

    for title, container in data.items():
        clues[title] = []

        # parse the clues from a string
        if isinstance(container, str):
            items = container.strip().split("\n")
            for item in items:
                clue = _parse_clue(item)
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

    # parse rows and right bars
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
            grid[x, y]["entry"] = char
            x += 1
        y += 1

    # parse columns and bottomn bars
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

    # parse the style information
    for y, row in enumerate(style):
        for x, char in enumerate(row):
            char = char.strip()
            if not char:
                continue
            if "style" not in grid[x, y]:
                grid[x, y]["style"] = {}
            grid[x, y]["style"][char] = styles.get(char, {})

    return width, height, grid


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
    width, height, grid = _parse_grid(grid_data, block, empty)
    puzzle["width"] = width
    puzzle["height"] = height
    puzzle["grid"] = grid

    # parse clues
    clues_data = data.get("clues", {})
    puzzle["clues"] = _parse_clues(clues_data)

    return puzzle
