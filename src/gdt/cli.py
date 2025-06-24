# -*- coding: utf-8 -*-
"""Command line interface for the Gene Dictionary Tool (gdt).

This module provides a command line interface to filter, standardize,
and manipulate GFF3 files using a Gene Dictionary Tool (GDT) file.
It supports various operations such as filtering GFF3 files based on
indexed TSV files, creating stripped versions of GDT files, and
standardizing gene names across GFF3 files.

"""

import argparse
import os
from pathlib import Path

from . import __version__, gdt_impl, gff3_utils, log_setup

C_RESET = "\033[0m"

GDT_BANNER = f"""           ╔═════════════════════════════╗
           ║   ██████╗ ██████╗ ████████╗ ║
           ║  ██╔════╝ ██╔══██╗╚══██╔══╝ ║
           ║  ██║  ███╗██║  ██║   ██║    ║
           ║  ██║   ██║██║  ██║   ██║    ║
           ║  ╚██████╔╝██████╔╝   ██║    ║
           ║   ╚═════╝ ╚═════╝    ╚═╝    ║
           ║    \033[34mGene Dictionary Tool{C_RESET}     ║
           ╚═════════════════════════════╝
🧬 \033[33mStandardizing gene names across organelle genomes{C_RESET} 🧬
                   Version: \033[32m{__version__}{C_RESET}"""


def filter_command(
    args: argparse.Namespace,
    log: log_setup.GDTLogger,
) -> None:
    """Command to filter GFF3 files based on a TSV file."""
    args.tsv = Path(args.tsv).resolve()

    if args.gdt:
        args.gdt = Path(args.gdt).resolve()

    log.debug(
        f"filter command: tsv: {args.tsv} | gdt: {args.gdt} | "
        f"keep_orfs: {args.keep_orfs} | workers: {args.workers} | "
        f"AN_column: {args.AN_column} | gff_suffix: {args.gff_suffix} | "
        f"query_string: {args.query_string}"
    )
    gff3_utils.filter_whole_tsv(
        log,
        args.tsv,
        args.gdt,
        args.keep_orfs,
        args.workers,
        args.AN_column,
        args.gff_suffix,
        args.query_string,
    )


def stripped_command(
    args: argparse.Namespace,
    log: log_setup.GDTLogger,
) -> None:
    """Command to create a stripped version of a GDT file."""
    log.info(
        f"stripped command: gdt_in: {args.gdt_in} | "
        f"gdt_out: {args.gdt_out} | "
        f"overwrite: {args.overwrite}"
    )
    args.gdt_in = Path(args.gdt_in).resolve()
    args.gdt_out = Path(args.gdt_out).resolve()

    if not args.gdt_in.exists():
        log.error(f"gdt not found: {args.gdt_in}")
        raise FileNotFoundError(f"GDT file not found: {args.gdt_in}")

    if args.gdt_out.exists() and not args.overwrite:
        log.error(
            f"gdt already exists, overwrite: {args.overwrite} | gdt: {args.gdt_out}"
        )
        raise FileExistsError(
            f"GDT file already exists: {args.gdt_out}. Use overwrite=True to overwrite."
        )

    gene_dict = gdt_impl.read_gdt(args.gdt_in)
    log.info("Info before stripping:")
    log_setup.log_gdt_info(log, gene_dict)

    stripped = gene_dict.create_stripped()
    stripped.update_info()

    log.info("\nNew Header:")
    for txt in stripped.header:
        log.info(txt)

    log.info("New Info:")
    log_setup.log_gdt_info(log, stripped)
    stripped.to_gdt(args.gdt_out, overwrite=args.overwrite)


def standardize_command(
    args: argparse.Namespace,
    log: log_setup.GDTLogger,
) -> None:
    """Command to standardize gene names in GFF3 files using a GDT file."""
    log.info(
        f"standardize command: gff: {args.gff} | tsv: {args.tsv} | "
        f"gdt: {args.gdt} | AN_column: {args.AN_column} | "
        f"gff_suffix: {args.gff_suffix} | query_string: {args.query_string} | "
        f"check: {args.check} | second_place: {args.second_place} | "
        f"gdt_tag: {args.gdt_tag} | error_on_missing: {args.error_on_missing} | "
        f"save_copy: {args.save_copy}"
    )
    args.gdt = Path(args.gdt).resolve()
    if args.gff:
        args.gff = Path(args.gff).resolve()

        if not args.gff.is_file():
            log.error(f"gff file not found: {args.gff}")

        if not args.gdt.exists():
            log.error(f"gdt file not found: {args.gdt}")
            raise FileNotFoundError(f"gdt file not found: {args.gdt}")

        gene_dict = gdt_impl.read_gdt(args.gdt)
        log.debug(f"Gene dictionary loaded from {args.gdt}")

        gff3_utils.standardize_gff3(
            log,
            args.gff,
            gene_dict,
            args.query_string,
            args.check,
            args.second_place,
            args.gdt_tag,
            args.error_on_missing,
            args.save_copy,
            True,
        )

    elif args.tsv:
        args.tsv = Path(args.tsv).resolve()
        gff3_utils.standardize_tsv(
            log,
            args.tsv,
            args.gdt,
            args.AN_column,
            args.gff_suffix,
            args.query_string,
            args.check,
            args.second_place,
            args.gdt_tag,
            args.error_on_missing,
            args.save_copy,
        )


def cli_run() -> None:
    """Command line interface for the Gene Dictionary Tool (gdt)."""
    # Global parser to add debug, log, and quiet flags to all subcommands
    global_flags = argparse.ArgumentParser(add_help=False)
    global_flags.add_argument(
        "--debug",
        required=False,
        default=False,
        action="store_true",
        help="Enable TRACE level in file, and DEBUG on console. "
        "Default: DEBUG level on file and INFO on console.",
    )
    global_flags.add_argument(
        "--log",
        required=False,
        default=None,
        type=str,
        help="Path to the log file. "
        "If not provided, a default log file will be created.",
    )
    global_flags.add_argument(
        "--quiet",
        required=False,
        default=False,
        action="store_true",
        help="Suppress console output. Default: console output enabled.",
    )

    main_parser = argparse.ArgumentParser(
        description=GDT_BANNER,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[global_flags],
        epilog=f"Source ~ \033[32mhttps://github.com/brenodupin/gdt{C_RESET}",
    )
    main_parser.add_argument(
        "--version",
        action="version",
        version=f"gdt {__version__}",
        help="Show the version of the gdt package.",
    )

    subparsers = main_parser.add_subparsers(
        dest="command",
        required=True,
    )

    filter_parser = subparsers.add_parser(
        "filter",
        help="Filter GFF3 files indexed through TSV file.",
        description="Filter GFF3 files that are indexed via TSV file, "
        "creating AN_missing_dbxref.txt and/or AN_missing_gene_dict.txt "
        "based on the provided GDT file.",
        parents=[global_flags],
    )
    filter_parser.add_argument(
        "--tsv",
        required=True,
        type=str,
        help="TSV file with indexed GFF3 files to filter.",
    )
    filter_parser.add_argument(
        "--AN-column",
        required=False,
        default="AN",
        type=str,
        help="Column name for NCBI Accession Number inside the TSV. Default: AN",
    )
    filter_parser.add_argument(
        "--gdt",
        required=False,
        default=False,
        type=str,
        help="GDT file to use for filtering. "
        "If not provided, an empty GeneDict (i.e GDT file) will be used.",
    )
    filter_parser.add_argument(
        "--keep-orfs",
        required=False,
        default=False,
        action="store_true",
        help="Keep ORFs. Default: exclude ORFs",
    )
    filter_parser.add_argument(
        "--workers",
        required=False,
        default=0,
        type=int,
        help="Number of workers to use. "
        f"Default: 0 (use all available cores: {os.cpu_count()})",
    )
    filter_parser.add_argument(
        "--gff-suffix",
        required=False,
        default=".gff3",
        type=str,
        help="Suffix for GFF files. Default: '.gff3'",
    )
    filter_parser.add_argument(
        "--query-string",
        required=False,
        default=gff3_utils.QS_GENE_TRNA_RRNA,
        type=str,
        help="Query string that pandas filter features in GFF. "
        f"Default: '{gff3_utils.QS_GENE_TRNA_RRNA}'",
    )

    stripped_parser = subparsers.add_parser(
        "stripped",
        help="Create a stripped version of a GDT file",
        description="Filter GeneGeneric's (#gn) and Dbxref's (#dx) out of a GDT file, "
        "keeping only GeneDescription (#gd) entries and their metadata.",
        parents=[global_flags],
    )
    stripped_parser.add_argument(
        "--gdt_in",
        "-gin",
        required=True,
        type=str,
        help="Input GDT file to strip.",
    )
    stripped_parser.add_argument(
        "--gdt_out",
        "-gout",
        required=True,
        type=str,
        help="New GDT file to create.",
    )
    stripped_parser.add_argument(
        "--overwrite",
        required=False,
        default=False,
        action="store_true",
        help="Overwrite output file, if it already exists. Default: False",
    )

    standardize_parser = subparsers.add_parser(
        "standardize",
        help="Standardize gene names in GFF3 files.",
        description="Standardize gene names across features in "
        "GFF3 files using a GDT file.",
        parents=[global_flags],
    )
    # mutually exclusive group for GFF or TSV input
    flag_group = standardize_parser.add_mutually_exclusive_group(required=True)
    flag_group.add_argument(
        "--gff",
        type=str,
        help="GFF3 file to standardize.",
    )
    flag_group.add_argument(
        "--tsv",
        type=str,
        help="TSV file with indexed GFF3 files to standardize.",
    )

    standardize_parser.add_argument(
        "--gdt",
        required=True,
        type=str,
        help="GDT file to use for standardization. ",
    )
    standardize_parser.add_argument(
        "--AN-column",
        required=False,
        default="AN",
        type=str,
        help="Column name for NCBI Accession Number inside the TSV. Default: AN",
    )
    standardize_parser.add_argument(
        "--gff-suffix",
        required=False,
        default=".gff3",
        type=str,
        help="Suffix for GFF files. Default: '.gff3'",
    )
    standardize_parser.add_argument(
        "--query-string",
        required=False,
        default=gff3_utils.QS_GENE_TRNA_RRNA,
        type=str,
        help="Query string that pandas filter features in GFF. "
        f"Default: '{gff3_utils.QS_GENE_TRNA_RRNA}'",
    )
    standardize_parser.add_argument(
        "--check",
        required=False,
        default=False,
        action="store_true",
        help="Just check for standardization issues, "
        "do not modify the GFF3 file. Default: False",
    )
    standardize_parser.add_argument(
        "--second-place",
        required=False,
        default=False,
        action="store_true",
        help="Add gdt-tag pair to the second place in the GFF3 file, after the ID. "
        "Default: False (add to the end of the attributes field).",
    )
    standardize_parser.add_argument(
        "--gdt-tag",
        required=False,
        default="gdt_label",
        type=str,
        help="Tag to use for the GDT key/value pair in the GFF3 file. "
        "Default: 'gdt_label='.",
    )
    standardize_parser.add_argument(
        "--error-on-missing",
        required=False,
        default=False,
        action="store_true",
        help="Raise an error if a feature is missing in the GDT file. "
        "Default: False (just log a warning and skip the feature).",
    )
    standardize_parser.add_argument(
        "--save-copy",
        required=False,
        default=False,
        action="store_true",
        help="Save a copy of the original GFF3 file with a .original suffix. "
        "Default: False (change inplace).",
    )

    args = main_parser.parse_args()

    if not args.quiet:
        print(GDT_BANNER)

    log = log_setup.setup_logger(args.debug, args.log, args.quiet)
    log.trace("CLI execution started")
    log.trace(f"call path: {Path().resolve()}")
    log.trace(f"cli  path: {Path(__file__)}")
    log.trace(f"args: {args}")

    match args.command:
        case "filter":
            filter_command(args, log)

        case "stripped":
            stripped_command(args, log)

        case "standardize":
            standardize_command(args, log)
