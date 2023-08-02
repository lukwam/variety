# -*- coding: utf-8 -*-
"""Clues class file."""
import logging

from puzzle.cluescontainer import CluesContainer


class Clues:
    """Clues class."""

    def __init__(self, puzzle):
        """Initialize the Clues class."""
        self.puzzle = puzzle
        self._clues = None
        self._containers = None
        self._from_dict()
        self.__containers_index = None

    @property
    def answers(self):
        """Return a list of clue answers used in the puzzle."""
        answers = {}
        for container in self._containers:
            for clue in container.clues:
                answers.extend(clue.answers)
        return answers

    @property
    def containers(self):
        """Return the containers."""
        return self._containers

    @property
    def entries(self) -> dict:
        """Return a dict of entries used in the puzzle."""
        entries = {}
        for container in self._containers:
            for entry, clue in container.entries.items():
                if entry in entries:
                    logging.warning(f"Duplicate entry: {entry}")
                entries[entry] = clue
        return entries

    @property
    def solutions(self):
        """Return a list of clue solutions used in the puzzle."""
        solutions = []
        for container in self._containers:
            for clue in container.clues:
                solutions.extend(clue.solutions)
        return solutions

    def __iter__(self):
        """Initialize a new iterator."""
        self.__containers_index = 0
        return self

    def __next__(self):
        """Return the next clue."""
        index = self.__containers_index
        if index >= len(self._containers):
            raise StopIteration
        self.__containers_index = index + 1
        return self._containers[index]

    def _from_dict(self):
        """Create the clues from a puzzle."""
        clues_data = self.puzzle.puzzle.get("clues", {})
        containers = []

        if isinstance(clues_data, dict):
            for title, clues in clues_data.items():
                containers.append(CluesContainer(title, clues, self.puzzle))

        elif isinstance(clues_data, list):
            for group in clues_data:
                containers.append(
                    CluesContainer(
                        group["name"],
                        group["clues"],
                        self.puzzle,
                        group,
                    ),
                )

        self._containers = containers

    def to_dict(self):
        """Return the clues as a dictionary."""
        clues = {}
        for container in self._containers:
            clues[container.title] = container.to_string()
        return clues

    def to_string(self):
        """Return the clues as a string."""
        output = []
        for container in self._containers:
            output.append(container.to_string())
        return "\n".join(output)
