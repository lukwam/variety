# -*- coding: utf-8 -*-
"""Clues Container class file."""
from puzzle.clue import Clue


class CluesContainer(object):
    """Clues Container class."""

    def __init__(self, title, clues, puzzle, settings={}):
        """Initialize the CluesContainer class."""
        self._clues = None
        self._title = None

        # control default behavior of clues
        self._reverse_grid_entries = False
        self._show_enumerations = None
        self._show_grid_entries = True
        self._show_grid_labels = None

        # set the settings
        if settings.get("show_enumerations"):
            self.enable_enumeration(settings["show_enumerations"])
        if settings.get("show_grid_entries") is False:
            self.disable_grid_entries()
        if settings.get("show_grid_labels") is False:
            self.disable_grid_labels()
        if settings.get("reverse_grid_entries") is True:
            self._reverse_grid_entries = True

        # set the clues
        self._clues = clues

        self.puzzle = puzzle

        # set the title (check for options in title)
        self._create_title(title)

        # create the clues from a multi-line text string or list of dicts
        self._create_clues(clues)

        # initialize the iterator
        self.__clues_index = None

    @property
    def clues(self):
        """Return the clues."""
        return self._clues

    @property
    def entries(self) -> dict:
        """Return the entries."""
        entries = {}
        for clue in self._clues:
            for entry in clue.entries:
                entries[entry] = clue
        return entries

    @property
    def has_starred_clues(self):
        """Return whether the container has starred clues."""
        for clue in self._clues:
            if clue.starred:
                return True
        return False

    @property
    def show_enumerations(self):
        """Return whether to show enumerations."""
        if self._show_enumerations is None:
            return self.puzzle.show_enumerations
        return self._show_enumerations

    @property
    def show_grid_entries(self):
        """Return whether to show grid entries."""
        return self._show_grid_entries

    @property
    def show_grid_labels(self):
        """Return whether to show grid labels."""
        if self._show_grid_labels is None:
            return self.puzzle.show_grid_labels
        return self._show_grid_labels

    @property
    def title(self):
        """Return the title."""
        return self._title

    def __iter__(self):
        """Initialize a new iterator."""
        self.__clues_index = 0
        return self

    def __next__(self):
        """Return the next clue."""
        index = self.__clues_index
        if index >= len(self._clues):
            raise StopIteration
        self.__clues_index = index + 1
        return self._clues[index]

    def _create_clues(self, raw_clues):
        """Create the clues."""
        if not raw_clues:
            return
        clues = []
        for raw_clue in self._parse_clues(raw_clues):
            clues.append(Clue(raw_clue, self))
        self._clues = clues
        return clues

    def _create_title(self, title):
        """Create the title."""
        if not isinstance(title, str):
            raise ValueError("Title must be a string.")

        # check for options in title
        if " ~ " in title:
            title, options = title.split(" ~ ")
            options = options.split(",")
            for option in options:
                option = option.strip()
                if option == "no-enumerations":
                    self.disable_enumeration()
                elif option == "no-grid-entries":
                    self.disable_grid_entries()
                elif option == "no-grid-labels":
                    self.disable_grid_labels()
                else:
                    raise ValueError(f"Invalid option: {option}")

        self._title = title.strip()

    def _parse_clues(self, clues):
        """Parse the clues."""
        if isinstance(clues, str):
            return clues.strip().split("\n")
        if isinstance(clues, list):
            return clues
        raise ValueError("Clues must be a list or string.")

    def disable_enumeration(self):
        """Disable enumeration."""
        self._show_enumerations = False

    def disable_grid_entries(self):
        """Disable grid entries."""
        self._show_grid_entries = False

    def disable_grid_labels(self):
        """Disable grid labels."""
        self._show_grid_labels = False

    def enable_enumeration(self, setting="answers"):
        """Enable enumeration."""
        self._show_enumerations = setting

    def enable_grid_labels(self):
        """Enable grid labels."""
        self._show_grid_labels = True

    def get_options(self):
        """Return the options."""
        options = []
        if self._show_enumerations is False:
            options.append("no-enumerations")
        if self._show_grid_labels is False:
            options.append("no-grid-labels")
        return sorted(options)

    @property
    def reverse_grid_entries(self):
        """Return the value of reverse grid entries."""
        return self._reverse_grid_entries

    def to_string(self):
        """Return the clues as a string."""
        output = []
        for clue in self.clues:
            output.append(clue.to_text())
        return "\n".join(output)

    def to_text(self):
        """Return the clues as a text string."""
        title = self.title

        # check for clue container options
        options = self.get_options()
        if options:
            title += f" ~ {', '.join(options)}"

        # create output
        output = [f"\n  {title}: |"]
        unclued = []
        for clue in self.clues:
            if clue.clue is None:
                unclued.append(clue)
                continue
            output.append(f"    {clue.to_text()}")
        if unclued:
            output.append("unclued:")
        for clue in unclued:
            output.append(f"  - {clue.to_text()}")
        return "\n".join(output)

    def to_yaml(self):
        """Return the clues as a YAML string."""
        output = [f"  {self.title}:"]
        for clue in self.clues:
            output.append(clue.to_yaml())
        return "\n".join(output)
