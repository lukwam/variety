# -*- coding: utf-8 -*-
"""Clue class file."""
import logging
import re

from puzzle.helpers import wrap_text


class Clue:
    """Clue class."""

    def __init__(self, clue, container):
        """Initialize a Clue instance."""
        # the clues container that this clue belongs to
        self.container = container
        self.puzzle = container.puzzle

        self._name = None
        self._clue = None

        self._answers = []
        self._entries = []
        self._solutions = []

        self._show_enumeration = None
        self._show_grid_entry = None
        self._show_grid_label = None
        self._starred = False

        # import from dict or string
        if isinstance(clue, dict):
            self._from_dict(clue)
        elif isinstance(clue, str):
            self._from_string(clue)
        else:
            raise ValueError("Clue must be a dictionary or string.")

        self.validate()

    @property
    def answers(self) -> list:
        """Return the answers."""
        return self._answers

    @property
    def clue(self):
        """Return the clue."""
        return self._clue

    @property
    def entries(self) -> list:
        """Return the entries, or the answers with special characters removed."""
        if not self.show_grid_entry:
            return []
        if not self._entries:
            return [re.sub("[- ]", "", e) for e in self._answers]
        return self._entries

    @property
    def label(self):
        """Return the clue label."""
        if ";" in self._name:
            return self._name.split(";")[1]
        return self.name

    @property
    def name(self):
        """Return the clue name."""
        name = self._name
        if not name:
            return ""
        if "|" in name:
            name = name.split("|")[0]
        if ";" in name:
            name = name.split(";")[0]
        return name

    @property
    def reverse_grid_entries(self):
        """Return whether to reverse grid entries."""
        return self.container.reverse_grid_entries

    @property
    def show_enumeration(self):
        """Return whether to show enumeration."""
        if self._show_enumeration is None:
            return self.container.show_enumerations
        return self._show_enumeration

    @property
    def show_grid_entry(self):
        """Return whether to show grid entries."""
        if self._show_grid_entry is None:
            return self.container.show_grid_entries
        return self._show_grid_entry

    @property
    def show_grid_label(self):
        """Return whether to show grid labels."""
        if self._show_grid_label is None:
            return self.container.show_grid_labels
        return self._show_grid_label

    @property
    def solutions(self) -> list:
        """Return the solutions."""
        return self._solutions

    @property
    def starred(self):
        """Return whether the clue is starred."""
        return self._starred

    @property
    def suffix(self):
        """Return the suffix of the clue name, if set."""
        if "|" in self._name:
            return self._name.split("|")[1]
        return None

    def __repr__(self):
        """Return the representation."""
        if not self.name and not self.clue:
            return f"Unclued: {self.answers}"
        name = self.name
        if self.starred:
            name = f"*{self.name}"
        if self.show_enumeration:
            enumeration = self.get_enumeration()
            return wrap_text(f"{name}. {self.clue} ({enumeration})", indent=4, width=80)
        return wrap_text(f"{name}. {self.clue}")

    def debug(self):
        """Return the full representation."""
        if not self.name and not self.clue:
            return f"Unclued: {self.answer}"
        answer = self.get_answer()
        enumeration = self.get_enumeration()
        return f"{self.name}: {self.clue} ({enumeration}) [{answer}]"

    def disable_enumeration(self):
        """Disable enumeration."""
        self._show_enumeration = False

    def disable_grid_label(self):
        """Disable grid label."""
        self._show_grid_label = False

    def enable_enumeration(self):
        """Enable enumeration."""
        self._show_enumeration = True

    def enable_grid_label(self):
        """Enable grid label."""
        self._show_grid_label = True

    def enable_star(self):
        """Enable star."""
        self._starred = True

    def _from_dict(self, clue):
        """Create a Clue object from a dictionary."""
        self._clue = clue.get("clue")

        # set the name
        self.set_name(clue.get("name"))

        # get answers
        answer = clue.get("answer")
        if answer:
            self._answers = [answer]
        else:
            self._answers = clue.get("answers", [])

        # get entries
        entry = clue.get("entry")
        if entry:
            self._entries = [entry]
        else:
            self._entries = clue.get("entries", [])

        # get solutions
        solution = clue.get("solution")
        if not solution:
            solution = clue.get("explanation")
        if solution:
            self._solutions = [solution]
        else:
            self._solutions = clue.get("solutions", [])
            if not self._solutions:
                self._solutions = clue.get("explanations", [])

        # check grid label visibility
        unlabeled = clue.get("unlabeled")
        if unlabeled is not None:
            self.disable_grid_label()

    def _from_string(self, clue_string):
        """Create a Clue object from a string."""
        data = self._parse_clue_string(clue_string)
        if not data:
            logging.error(
                f"Clue does not match expected format: {clue_string}",
            )
            return

        # get parsed clue data
        name = data.get("name")
        clue = data.get("clue")
        answer = data.get("answer")
        solution = data.get("solution", "")

        # parse the answer/entry info
        answer_data = self._parse_answer_string(answer)
        answers = answer_data.get("answers", [])
        entries = answer_data.get("entries", [])

        # parse the solution info
        solutions = self._parse_solution_string(solution)

        # set values in the clue object
        self.set_name(name)
        self.set_clue(clue)
        self.set_answers(answers)
        self.set_entries(entries)
        self.set_solutions(solutions)

    def _parse_answer_string(self, answer_string) -> dict:
        """Parse an answer string."""
        data = {
            "answers": [],
            "entries": [],
        }

        # initialize answer and entry
        answer_part = answer_string.strip()
        entry__part = ""

        # split the answer into answer and entry parts
        parts = answer_part.split("|")
        if len(parts) == 2:
            answer_part, entry__part = parts

        # extract answers from string
        for answer in answer_part.split(";"):
            answer = answer.strip()
            if answer:
                data["answers"].append(answer)

        # extract entries from string
        for entry in entry__part.split(";"):
            entry = entry.strip()
            if entry:
                data["entries"].append(entry)

        return data

    def _parse_clue_string(self, clue_string) -> dict:
        """Parse a clue string."""
        name = r"^(?P<name>[^\.]+)\."
        clue = r"(?P<clue>.+)"
        ans = r"(?P<answer>[- A-Z0-9★;\|]+)"
        sol = r"(?P<solution>.*)"

        # all parts are provided
        results = re.match(f"{name} {clue} ~ {ans} ~ {sol}", clue_string)
        if results:
            return results.groupdict()

        # only solution is missing
        results = re.match(f"{name} {clue} ~ {ans}", clue_string)
        if results:
            return results.groupdict()

        # solution and answer are missing
        results = re.match(f"{name} {clue}", clue_string)
        if results:
            return results.groupdict()

        # clue, solution and answer are missing
        results = re.match(f"{name}", clue_string)
        if results:
            return results.groupdict()

        # give up
        return {}

    def _parse_solution_string(self, solution_string) -> list:
        """Parse a solution string."""
        solutions = []
        for solution in solution_string.split(";"):
            solution = solution.strip().replace("<i>", '"').replace("</i>", '"')
            if solution:
                solutions.append(solution)
        return solutions

    def get_answer(self):
        """Get the answer."""
        if self.answer:
            return self.answer
        return ", ".join(self._answers)

    def get_answers(self):
        """Get the answers."""
        if self.answer:
            return [self.answer]
        return self._answers

    def get_entry(self):
        """Get the entry."""
        if self.entry:
            return self.entry
        if self.entries:
            return ", ".join(self.entries)
        return self.get_answer()

    def get_entries(self):
        """Get the entries."""
        logging.warning(
            "Clue.get_entries is deprecated. Use Clue.get_entry instead.",
        )
        if self.entry:
            return [self.entry]
        if self.entries:
            return self.entries
        return [e.replace(" ", "") for e in self.get_answers()]

    def get_enumeration(self):
        """Get the enumeration of the answer(s)."""
        if self.show_enumeration == "entries":
            answers = self.entries
        else:
            answers = self.answers

        outputs = []
        for answer in answers:
            num = 0
            output = ""
            for char in answer:
                # count alpha characters
                if char.isalpha():
                    num += 1
                # replace spaces with commas
                elif char == " ":
                    output += f"{num},"
                    num = 0
                # keep other characters as they are
                else:
                    output += f"{num}{char}"
                    num = 0
            output += f"{num}"
            outputs.append(output)
        return ",".join(outputs)

    def get_solution(self):
        """Get the solution."""
        # logging.warning("Clue.get_solution is deprecated. Use Clue.solutions instead.")
        return "; ".join(self._solutions)

    def set_answers(self, answers):
        """Set the answers."""
        # TODO: add validation for incoming answers
        self._answers = answers

    def set_clue(self, clue):
        """Set the clue."""
        self._clue = clue

    def set_entries(self, entries):
        """Set the entries."""
        # TODO: add validation for incoming entries
        if self.reverse_grid_entries:
            if not entries:
                entries = self.answers
            for n, entry in enumerate(entries):
                entries[n] = entry[::-1]
        self._entries = entries

    def set_name(self, name):
        """Set the name."""
        if not name:
            return
        if isinstance(name, int):
            name = str(name)
        if name.startswith("*"):
            self.enable_star()
            name = name[1:]
        self._name = name

    def set_solutions(self, solutions):
        """Set the solutions."""
        # TODO: add validation for incoming solutions
        self._solutions = solutions

    @property
    def raw(self):
        """Return a raw representation of the entry."""
        answers = ';'.join(self._answers)
        entries = ';'.join(self._entries)
        solutions = ';'.join(self._solutions)

        if entries:
            answers = f"{answers}|{entries}"

        return f"{self._name}. {self._clue} ~ {answers} ~ {solutions}"

    def to_text(self):
        """Return a text representation of the entry."""
        answer = ";".join(self.answers)
        entry = ";".join(self.entries)
        if entry:
            answer = f"{answer}|{entry}"
        solution = ";".join(self.solutions)
        return f"{self.name}. {self.clue} ~ {answer} ~ {solution}"

    def to_yaml(self):
        """Return a yaml representation of the entry."""
        output = [f"    - name: {self._name}"]
        if self._clue:
            output.append(f"      clue: {self._clue}")
        if self._answers:
            output.append(f"      answers: {';'.join(self._answers)}")
        if self._entries:
            output.append(f"      entries: {';'.join(self._entries)}")
        if self._solutions:
            output.append(f"      solutions: {';'.join(self._solutions)}")
        return "\n".join(output)

    def validate(self):
        """Validate the clue."""
        if not self.name:
            self.puzzle.error(
                f"Clue does not have a name: {self.clue}", "clue_format",
            )
        if not self.clue:
            self.puzzle.error(
                f"Clue does not have a clue: {self.clue}", "clue_format",
            )
        if not self.answers:
            self.puzzle.error(
                f"Clue does not have an answer: {self.clue}", "clue_format",
            )
        if not self.solutions:
            self.puzzle.error(
                f"Clue does not have a solution: {self.clue}", "clue_format",
            )
