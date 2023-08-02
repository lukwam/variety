# -*- coding: utf-8 -*-
"""Helpers module."""
import textwrap
from html.parser import HTMLParser
from io import StringIO

import yaml


class MLStripper(HTMLParser):
    """ML Stripper class."""

    def __init__(self):
        """Initialize the ML Stripper class."""
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, data):
        """Handle data."""
        self.text.write(data)

    def get_data(self):
        """Get data."""
        return self.text.getvalue()


def str_presenter(dumper, data):
    """Configure YAML multi-line string representation."""
    if len(data) > 40:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


def strip_tags(html):
    """Strip HTML tags from a string."""
    stripper = MLStripper()
    stripper.feed(html)
    return stripper.get_data()


def wrap_text(text, indent=0, width=80):
    """Wrap text at a specified width."""
    paragraphs = []
    for paragraph in text.split("\n\n"):
        wrapped = "\n".join(
            textwrap.wrap(
                paragraph, width, subsequent_indent=" " * indent,
            ),
        )
        paragraphs.append(wrapped)
    return "\n\n".join(paragraphs)


def yaml_dump(data):
    """Dump data as YAML."""
    yaml.add_representer(str, str_presenter)
    yaml.representer.SafeRepresenter.add_representer(str, str_presenter)
    return yaml.dump(
        data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
