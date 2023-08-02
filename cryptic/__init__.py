# -*- coding: utf-8 -*-
"""Cryptic is a Python library for working with cryptic crossword puzzles."""

__title__ = 'cryptic'
__version__ = '0.0.1'
__author__ = 'Lukas Karlsson'
__email__ = 'lukwam@gmail.com'
__license__ = 'MIT'
__copyright__ = 'Copyright 2023 Lukas Karlsson'

from cryptic.core import CrypticCrossword, CrypticClues, CrypticCluesContainer
from cryptic.format_hex import from_hex, to_hex
from cryptic.format_xml import to_xml
