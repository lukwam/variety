# -*- coding: utf-8 -*-
"""Settings class file."""


class Settings:
    """Settings class."""
    _defaults = {}
    _validation = {}

    def __init__(self, settings):
        """Initialize the Settings class."""
        self._settings = {}
        for key in settings:
            self.set(key, settings[key])

    def get(self, key, default=None):
        """Return the setting."""
        if key not in self._defaults:
            raise ValueError(f"Undefined setting: {key}")
        if key in self._settings:
            return self._settings.get(key, default)
        return self._defaults.get(key, default)

    def set(self, key, value):
        """Set the setting."""
        if not self.validate(key, value):
            return
        self._settings[key] = value

    def to_dict(self):
        """Return the settings as a dict."""
        return self._settings

    def validate(self, key, value):
        """Validate the setting."""
        if key not in self._defaults:
            raise ValueError(f"Undefined setting: {key}")
        if key not in self._validation:
            return True
        expected_values = self._validation[key]
        if value not in expected_values:
            raise ValueError(
                f"Invalid value for setting: {key} [expected: {expected_values}]",
            )
        return True


class PuzzleSettings(Settings):
    """Puzzle settings class."""
    _defaults = {
        "clue_columns": 2,
        "show_enumerations": "answers",
        "show_grid_bars": "all",
        "show_grid_border": False,
        "show_grid_entries": True,
        "show_grid_labels": True,
        "show_grid_lines": True,
        "show_starred_entries_in_grid": True,
        "status": "draft",
    }
    _validation = {
        "clue_columns": [
            1,  # clues are 1 column
            2,  # clues are 2 columns
            3,  # clues are 3 columns
            4,  # clues are 4 columns
            5,  # clues are 5 columns
        ],
        "show_enumerations": [
            "answers",  # show enumerations based on the answer (default)
            "entries",  # show enumerations based on the entry
            True,       # show enumerations based on the answer
            False,      # do not show enumerations
        ],
        "show_grid_bars": {
            "all",       # show all grid bars (default)
            "puzzle",    # show grid bars for puzzle only
            "solution",  # show grid bars for solution only
            True,        # show all grid bars
            False,       # do not show grid bars
        },
        "show_grid_border": {
            True,      # show grid border
            False,     # do not show grid border (default)
        },
        "show_grid_entries": [
            True,       # entries appear in the grid (default)
            False,      # entries do not appear in the grid
        ],
        "show_grid_labels": [
            True,       # show grid labels (default)
            False,      # do not show grid labels
        ],
        "show_grid_lines": {
            True,      # show grid lines (default)
            False,     # do not show grid lines
        },
        "show_starred_entries_in_grid": [
            True,       # show starred entries in the grid (default)
            False,      # do not show starred entries in the grid
        ],
        "status": [
            "draft",      # puzzle is in draft mode
            "published",  # puzzle is published
        ],
    }
