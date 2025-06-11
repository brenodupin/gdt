# -*- coding: utf-8 -*-

from . import logger_setup
from . import gene_dict_impl
from . import tsv_filter
from . import gff3_utils
from gdt import __version__

from pathlib import Path
import argparse

c_BLUE = "\033[34m"
c_YELLOW = "\033[33m"
c_GREEN = "\033[32m"
c_RESET = "\033[0m"

GDT_BANNER = f"""
           ╔════════════════════════════════╗
           ║    ██████╗ ██████╗ ████████╗   ║
           ║   ██╔════╝ ██╔══██╗╚══██╔══╝   ║
           ║   ██║  ███╗██║  ██║   ██║      ║
           ║   ██║   ██║██║  ██║   ██║      ║
           ║   ╚██████╔╝██████╔╝   ██║      ║
           ║    ╚═════╝ ╚═════╝    ╚═╝      ║
           ║    {c_BLUE}Gene Dictionary Tool{c_RESET}        ║
           ╚════════════════════════════════╝
🧬 {c_YELLOW}Standardizing gene names across organelle genomes{c_RESET} 🧬
                   Version: {c_GREEN}{__version__}{c_RESET}
"""


def cli_run() -> None:
    """Command line interface for the Gene Dictionary Tool (gdt)"""

    # Global parser for the command line interface
    gp = argparse.ArgumentParser(add_help=False)
    gp.add_argument(
        "--debug",
        required=False,
        default=False,
        action="store_true",
        help="Enable TRACE level in file log, and DEBUG on console. "
        "Default: False (DEBUG level on file and INFO on console)",
    )

    gp.add_argument(
        "--log",
        required=False,
        default=None,
        type=str,
        help="Path to the log file. "
        "If not provided, a default log file will be created.",
    )
    gp.add_argument(
        "--quiet",
        required=False,
        default=False,
        action="store_true",
        help="Suppress console output. " "Default: False (console output enabled)",
    )

    parser = argparse.ArgumentParser(
        description="Gene Dictionary Tool (gdt) command line interface",
        parents=[gp],
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the version of the gdt package",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    subparsers.required = True

    filter_parser = subparsers.add_parser(
        "filter",
        help="Filter GFF3 files index in a TSV file",  # Brief help for main command list
        description="Filter GFF3 files that are indexed in a TSV file into AN_missing_dbxref or AN_missing_gene_dict categories",
        parents=[gp],
    )
    filter_parser.add_argument("--tsv", required=True, help="TSV file to filter")
    filter_parser.add_argument(
        "--AN-column",
        required=False,
        default="AN",
        type=str,
        help="Column name for NCBI Accession Number. Default: AN",
    )
    filter_parser.add_argument(
        "--gdt",
        required=False,
        default=False,
        help="GDT file to use for filtering. "
        "If not provided, an empty gene_dict will be used.",
    )
    filter_parser.add_argument(
        "--keep-orfs",
        required=False,
        default=False,
        action="store_true",
        help="Don't discard ORFs. Default: False (discard ORFs)",
    )
    filter_parser.add_argument(
        "--workers",
        required=False,
        default=0,
        type=int,
        help="Number of workers to use. Default: 0 (use all available cores)",
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
        help="Pandas query string to filter GFF3 files. "
        f"Default: '{gff3_utils.QS_GENE_TRNA_RRNA}'",
    )

    stripped_parser = subparsers.add_parser(
        "stripped", help="Create a stripped GDT version of a GDT file", parents=[gp]
    )
    stripped_parser.add_argument(
        "--gdt_in", "-gin", required=True, help="Input GDT file to strip"
    )
    stripped_parser.add_argument(
        "--gdt_out", "-gout", required=True, help="Output GDT file to write"
    )
    stripped_parser.add_argument(
        "--overwrite",
        required=False,
        default=False,
        action="store_true",
        help="Overwrite output file if it exists. Default: False",
    )

    test_parser = subparsers.add_parser("test", help="Test command", parents=[gp])
    args = parser.parse_args()

    if not args.quiet:
        print(GDT_BANNER)

    log = logger_setup.setup_logger(args.debug, args.log, args.quiet)
    log.debug("CLI run called.")
    log.debug(f"exec path: {Path().resolve()}")
    log.debug(f"cli  path: {Path(__file__)}")
    log.debug(f"args: {args}")

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
        tsv_filter.filter_whole_tsv(
            log,
            args.tsv,
            args.gdt,
            args.keep_orfs,
            args.workers,
            args.AN_column,
            args.gff_suffix,
            args.query_string,
        )

    elif args.command == "write":
        log.info(f"Write command: gdt: {args.gdt} | out: {args.out}")
        gd = gene_dict_impl.create_gene_dict(args.gdt, max_an_sources=0)
        gene_dict_impl.write_gdt_file(gd, args.out, overwrite=True)

    elif args.command == "test":
        log.info(f"Test command: {args}")
        pass

    elif args.command == "stripped":
        log.info(
            f"Stripped command: gdt_in: {args.gdt_in} | gdt_out: {args.gdt_out} | overwrite: {args.overwrite}"
        )
        args.gdt_in = Path(args.gdt_in).resolve()
        args.gdt_out = Path(args.gdt_out).resolve()

        if args.gdt_in.exists():
            log.debug(f"Input GDT file: {args.gdt_in}")
            log.debug(f"Output GDT file: {args.gdt_out}")
            gene_dict_impl.create_stripped_gdt(
                args.gdt_in, args.gdt_out, overwrite=args.overwrite
            )
        else:
            log.error(f"Input GDT file does not exist: {args.gdt_in}")
            raise FileNotFoundError(f"GDT file not found: {args.gdt_in}")
