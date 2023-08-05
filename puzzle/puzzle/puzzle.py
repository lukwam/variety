# -*- coding: utf-8 -*-
"""Puzzle class file."""
import datetime
import logging
import textwrap

import yaml

from puzzle.clue import Clue
from puzzle.clues import Clues
from puzzle.cluescontainer import CluesContainer
from puzzle.grid import Grid
from puzzle.helpers import strip_tags
from puzzle.helpers import wrap_text
from puzzle.helpers import yaml_dump
from puzzle.settings import PuzzleSettings


class Puzzle:
    """Puzzle class."""

    required_fields = [
        "author",
        "clues",
        "date",
        "grid",
        "instructions",
        "publication",
        "title",
    ]

    optional_fields = [
        "editor",
        "id",
        "issue",
        "number",
        "settings",
        "solution",
        "unclued",
    ]

    def __init__(self, puzzle):
        """Initialize the Puzzle class."""
        if not puzzle:
            raise ValueError("Puzzle cannot be empty.")
        if not isinstance(puzzle, dict):
            raise ValueError(
                f"Puzzle must be a dictionary. Received {type(puzzle)}.",
            )
        if not isinstance(puzzle, dict):
            raise ValueError(
                f"Puzzle must be a dictionary. Received {type(puzzle)}.",
            )
        self.id = puzzle.get("id")
        self.puzzle = puzzle

        # puzzle metadata
        self._author = None
        self._date = None
        self._editor = None

        self._issue = None
        self._number = None
        self._publication = None
        self._title = None

        # puzzle text content
        self._instructions = None
        self._solution = None

        # puzzle content objects
        self._clues = None
        self._grid = None
        self._settings = None
        self._unclued = None

        # error handling
        self._errors = {}

        # load data a from dictionary to initialize the puzzle object
        self._from_dict()
        self._validate()

    @property
    def answers(self):
        """Return the answers for all clues in the puzzle."""
        return self._clues.answers

    @property
    def author(self):
        """Return the author."""
        return self._author

    @property
    def clues(self):
        """Return the clues."""
        return self._clues

    @property
    def clue_columns(self):
        """Show number of columns to display for clues."""
        return self.get_setting("clue_columns", 2)

    @property
    def columns(self):
        """Return the columns of the grid."""
        return self._grid.columns

    @property
    def date(self):
        """Return the date."""
        return self._date

    @property
    def editor(self):
        """Return the editor."""
        return self._editor

    @property
    def entries(self):
        """Return the entries all clues in the puzzle."""
        return self._clues.entries

    def error(self, error, type=None):
        """Add an error."""
        if not error:
            return
        if not type:
            type = "other"
        if type not in self._errors:
            self._errors[type] = []
        self._errors[type].append(error)

    @property
    def errors(self):
        """Return the errors."""
        return self._errors

    @property
    def grid(self):
        """Return the grid."""
        return self._grid

    @property
    def has_starred_clues(self):
        """Return true if the puzzle includes clues labeled with an asterisk."""
        for container in self._clues:
            if container.has_starred_clues:
                return True
        return False

    @property
    def height(self):
        """Return the height of the grid."""
        return len(self.rows)

    @property
    def instructions(self):
        """Return the instructions."""
        return self._instructions

    @property
    def issue(self):
        """Return the issue."""
        return self._issue

    @property
    def number(self):
        """Return the number."""
        return self._number

    @property
    def publication(self):
        """Return the publication."""
        return self._publication

    @property
    def rows(self):
        """Return the rows of the grid."""
        return self._grid.rows

    @property
    def settings(self):
        """Return the settings."""
        return self._settings

    @property
    def show_enumerations(self):
        """Show enumerations for clues."""
        return self.get_setting("show_enumerations", "answers")

    @property
    def show_grid_bars(self):
        """Show grid bars for clues."""
        return self.get_setting("show_grid_bars", "all")

    @property
    def show_grid_border(self):
        """Show grid border for clues."""
        return self.get_setting("show_grid_border", True)

    @property
    def show_grid_labels(self):
        """Show grid labels for clues."""
        return self.get_setting("show_grid_labels", True)

    @property
    def show_grid_lines(self):
        """Show grid lines for clues."""
        return self.get_setting("show_grid_lines", True)

    @property
    def solution(self):
        """Return the text of the puzzle solution."""
        return self._solution

    @property
    def solutions(self):
        """Return the solutions for all clues in the puzzle."""
        return self._clues.solutions

    @property
    def status(self):
        """Return the status for all clues in the puzzle."""
        return self.get_setting("status", "draft")

    @property
    def title(self):
        """Return the title."""
        return self._title

    @property
    def unclued(self):
        """Return the unclued squares."""
        return self._unclued

    @property
    def width(self):
        """Return the width of the grid."""
        return len(self.columns)

    def __repr__(self):
        """Return the representation."""
        return (
            f"{self.date}: {self.title}"
            f" by {self.author}"
            f" ({self.publication})"
        )

    def _check_extra_fields(self, puzzle):
        """Check for extra fields."""
        for field in puzzle:
            if field not in self.required_fields + self.optional_fields:
                logging.warning(f"Extra field: {field}")

    def _check_required_fields(self, puzzle):
        """Check for required fields."""
        for field in self.required_fields:
            if field not in puzzle:
                raise ValueError(f"Missing required field: {field}")

    def _from_dict(self, puzzle=None):
        """Create a puzzle from a dictionary."""
        if puzzle is None:
            puzzle = self.puzzle

        # validate input data
        self._check_required_fields(puzzle)
        self._check_extra_fields(puzzle)

        # set puzzle metadata
        self._set_author(puzzle)
        self._set_date(puzzle)
        self._set_editor(puzzle)
        self._set_issue(puzzle)
        self._set_number(puzzle)
        self._set_publication(puzzle)
        self._set_title(puzzle)

        # get settings that crontrol some puzzle behavior
        self._set_settings(puzzle)

        # set puzzle text content
        self._set_instructions(puzzle)
        self._set_solution(puzzle)

        # set puzzle content objects
        self._set_clues(puzzle)
        self._set_grid(puzzle)
        self._set_unclued(puzzle)

    def _set_author(self, puzzle):
        """Set the author."""
        author = puzzle.get("author")
        if author and not isinstance(author, str):
            raise ValueError(
                f"Author must be a string. Received {type(author)}.",
            )
        self._author = author

    def _set_clues(self, puzzle):
        """Set the clues."""
        clues = puzzle.get("clues", {})
        if not clues:
            raise ValueError("Clues cannot be empty.")
        if clues and not isinstance(clues, dict) and not isinstance(clues, list):
            raise ValueError(
                f"Clues must be a dict or a list. Received {type(clues)}.",
            )
        self._clues = Clues(self)

    def _set_date(self, puzzle):
        """Set the date."""
        date = puzzle.get("date")
        if date and not isinstance(date, datetime.date):
            raise ValueError(f"Date must be a date. Received {type(date)}.")
        self._date = date

    def _set_editor(self, puzzle):
        """Set the editor."""
        editor = puzzle.get("editor")
        if editor and not isinstance(editor, str):
            raise ValueError(
                f"Editor must be a string. Received {type(editor)}.",
            )
        self._editor = editor

    def _set_grid(self, puzzle):
        """Set the grid."""
        grid = puzzle.get("grid")
        if not grid:
            raise ValueError("Grid cannot be empty.")
        if grid and not isinstance(grid, dict):
            raise ValueError(f"Grid must be a dict. Received {type(grid)}.")
        rows = grid.get("rows")
        if not isinstance(rows, list):
            raise ValueError(f"Rows must be a list. Received {type(rows)}.")
        columns = grid.get("columns")
        if not isinstance(columns, list):
            raise ValueError(
                f"Columns must be a list. Received {type(columns)}.",
            )
        self._grid = Grid(self)

    def _set_instructions(self, puzzle):
        """Set the instructions."""
        instructions = puzzle.get("instructions")
        if instructions and not isinstance(instructions, str):
            raise ValueError(
                f"Instructions must be a string. Received {type(instructions)}.",
            )
        self._instructions = wrap_text(instructions)

    def _set_issue(self, puzzle):
        """Set the issue."""
        issue = puzzle.get("issue")
        if issue and not isinstance(issue, str):
            raise ValueError(
                f"Issue must be a string. Received {type(issue)}.",
            )
        self._issue = issue

    def _set_number(self, puzzle):
        """Set the number."""
        number = puzzle.get("number")
        if number and not isinstance(number, int):
            raise ValueError(
                f"Number must be an integer. Received {type(number)}.",
            )
        self._number = number

    def _set_publication(self, puzzle):
        """Set the publication."""
        publication = puzzle.get("publication")
        if publication and not isinstance(publication, str):
            raise ValueError(
                f"Publication must be a string. Received {type(publication)}.",
            )
        self._publication = publication

    def _set_settings(self, puzzle):
        """Set the settings."""
        settings = puzzle.get("settings", {})
        if settings and not isinstance(settings, dict):
            raise ValueError(
                f"Settings must be a dictionary. Received {type(settings)}.",
            )
        self._settings = PuzzleSettings(settings)

    def _set_solution(self, puzzle):
        """Set the solution."""
        solution = puzzle.get("solution")
        if solution and not isinstance(solution, str):
            raise ValueError(
                f"Solution must be a string. Received {type(solution)}.",
            )
        self._solution = solution

    def _set_title(self, puzzle):
        """Set the title."""
        title = puzzle.get("title")
        if title and not isinstance(title, str):
            raise ValueError(
                f"Title must be a string. Received {type(title)}.",
            )
        self._title = title

    def _set_unclued(self, puzzle):
        """Set the unclued."""
        unclued = puzzle.get("unclued", [])
        if unclued and not isinstance(unclued, list):
            raise ValueError(
                f"Unclued must be a list. Received {type(unclued)}.",
            )
        self._unclued = unclued

    def _validate(self):
        """Validate the puzzle."""
        clue_entries = self.entries
        grid_entries = self._grid.entries

        extra_clues = []
        missing_clues = []
        for entry in clue_entries:
            if entry not in grid_entries and entry not in self._unclued:
                extra_clues.append(entry)
        for entry in grid_entries:
            if entry not in clue_entries and entry not in self._unclued:
                missing_clues.append(entry)

        if extra_clues:
            self.error(f"Extra clues: {sorted(extra_clues)}", "extra_clues")
        if missing_clues:
            self.error(
                f"Missing clues: {sorted(missing_clues)}", "missing_clues",
            )

    def get_setting(self, setting, default=None):
        """Get a setting."""
        return self._settings.get(setting, default)

    def to_dict(self):
        """Convert the puzzle to a dictionary."""
        puzzle = {
            "title": self.title,
            "author": self.author,
            "date": self.date,
            "publication": self.publication,
            "editor": self.editor if self.editor else None,
            "issue": self.issue if self.issue else None,
            "number": self.number if self.number else None,
            "instructions": self.instructions if self.instructions else None,
            "solution": wrap_text(self.solution) if self.solution else None,
            "grid": self.grid.to_dict(),
            "clues": self.clues.to_dict(),
            "settings": self.settings.to_dict(),
            "unclued": self.unclued,
        }
        return puzzle

    def to_yaml(self):
        """Convert the puzzle to YAML."""
        # return yaml_dump(self.puzzle)
        return yaml_dump(self.to_dict())

    #
    # Display
    #
    def display_puzzle(self, line_length=80):
        """Display the puzzle."""
        # display header
        print(f"\"{self.title}\" by {self.author}")
        print(f"published on {self.date} in \"{self.publication}\"")

        # display grid
        self._grid.display_grid()

        # display optional instructions
        if self.instructions:
            print(strip_tags(self.instructions))

        # check for * padding
        padding = ""
        if self.has_starred_clues:
            padding = " "

        # display clues
        print("\n[CLUES]")
        for container in self._clues:
            print(f"\n{container.title}:")
            for clue in container:
                if clue.clue:
                    print(f"*{clue}" if clue.starred else f"{padding}{clue}")

    def display_solution(self, line_length=80):
        """Display the solution."""
        print("\n[SOLUTION]")

        self._grid.display_grid(show_answers=True)

        if self.solution:
            solution = ""
            for paragraph in self.solution.split("\n"):
                solution += "\n".join(textwrap.wrap(paragraph, line_length))
            print(strip_tags(solution))

        for container in self._clues:
            output = f"{container.title}:"
            unclued_answers = []
            for clue in container:
                if not clue.name:
                    for answer in clue.get_answers():
                        unclued_answers.append(answer)
                    continue
                solution = clue.get_solution()
                if solution:
                    output += f" {clue.name}. {solution}"
            print("\n" + "\n".join(textwrap.wrap(output, line_length)))

            if unclued_answers:
                print("\nUnclued: " + ", ".join(unclued_answers))
