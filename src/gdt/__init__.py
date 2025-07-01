# -*- coding: utf-8 -*-
"""GDT (Gene Dict Tool) package.

This package provides tools for working with gene dictionaries, including
GFF3 file parsing, gene dictionary manipulation, and logging setup.
"""

__version__ = "1.1.0"

from .gdict import (
    DbxrefGeneID,
    GeneDescription,
    GeneDict,
    GeneDictInfo,
    GeneGeneric,
    create_empty_gdict,
    natural_sort,
    natural_sort_key,
    read_gdict,
    time_now,
)
from .gff3_utils import (
    GFF3_COLUMNS,
    QS_GENE,
    QS_GENE_TRNA_RRNA,
    GFFPathBuilder,
    check_gff_in_tsv,
    check_single_an,
    filter_orfs,
    filter_whole_tsv,
    load_gff3,
    standardize_gff3,
    standardize_tsv,
)
from .log_setup import (
    TRACE,
    GDTLogger,
    create_dev_logger,
    create_simple_logger,
    log_info,
    setup_logger,
)
