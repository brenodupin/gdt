# -*- coding: utf-8 -*-
"""GDT (Gene Dict Tool) package.

This package provides tools for working with gene dictionaries, including
GFF3 file parsing, gene dictionary manipulation, and logging setup.
"""

__version__ = "0.1.3"

from .gdt_impl import *
from .gff3_utils import *
from .logger_setup import *
