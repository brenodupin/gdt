# -*- coding: utf-8 -*-

import os
from . import logger_setup
from . import gene_dict_impl
from . import gff3_utils
from gdt import __version__

from pathlib import Path
import argparse

c_RESET = "\033[0m"

GDT_BANNER = f"""           ╔════════════════════════════════╗
           ║    ██████╗ ██████╗ ████████╗   ║
           ║   ██╔════╝ ██╔══██╗╚══██╔══╝   ║
           ║   ██║  ███╗██║  ██║   ██║      ║
           ║   ██║   ██║██║  ██║   ██║      ║
           ║   ╚██████╔╝██████╔╝   ██║      ║
           ║    ╚═════╝ ╚═════╝    ╚═╝      ║
           ║    \033[34mGene Dictionary Tool{c_RESET}        ║
           ╚════════════════════════════════╝
🧬 \033[33mStandardizing gene names across organelle genomes{c_RESET} 🧬
                   Version: \033[32m{__version__}{c_RESET}"""


def cli_run() -> None:
    """Command line interface for the Gene Dictionary Tool (gdt)"""

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
        epilog=f"Source ~ \033[32mhttps://github.com/brenodupin/gdt{c_RESET}",
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
        "keeping only GeneDescription (#gd) entries and its metadata.",
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

    subparsers.add_parser("test", help="Test command", parents=[gp])
    args = parser.parse_args()

    if not args.quiet:
        print(GDT_BANNER)

    log = logger_setup.setup_logger(args.debug, args.log, args.quiet)
    log.trace("CLI run called.")
    log.trace(f"exec path: {Path().resolve()}")
    log.trace(f"cli  path: {Path(__file__)}")
    log.trace(f"args: {args}")

    if args.command == "filter":
        args.tsv = Path(args.tsv).resolve()

        if args.gdt:
            args.gdt = Path(args.gdt).resolve()

        log.debug(
            f"Filter command: tsv: {args.tsv} | gdt: {args.gdt} | "
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

    elif args.command == "stripped":
        log.info(
            f"Stripped command: gdt_in: {args.gdt_in} | "
            f"gdt_out: {args.gdt_out} | "
            f"overwrite: {args.overwrite}"
        )
        args.gdt_in = Path(args.gdt_in).resolve()
        args.gdt_out = Path(args.gdt_out).resolve()

        if args.gdt_in.exists():
            gene_dict_impl.create_stripped_gdt(
                args.gdt_in, args.gdt_out, overwrite=args.overwrite
            )
        else:
            log.error(f"Input GDT file does not exist: {args.gdt_in}")
            raise FileNotFoundError(f"GDT file not found: {args.gdt_in}")

    elif args.command == "test":
        log.info(f"Test command: {args}")
