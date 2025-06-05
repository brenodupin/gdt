# -*- coding: utf-8 -*-

from . import logger_setup
from . import gene_dict_impl
from . import tsv_filter
from . import gff3_utils

from pathlib import Path
import argparse


def cli_run():
    """Test function for CLI."""
    # TODO pick a better description
    parser = argparse.ArgumentParser(
        description="Gene Dictionary Tool (GDT) command line interface"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    subparsers.required = True

    # TODO pick a better description
    filter_parser = subparsers.add_parser(
        "filter", help="Filter tsv ans into AN_missing_dbxref or AN_missing_gene_dict"
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
        help="GDT filed that will be used as base",
    )
    filter_parser.add_argument(
        "--orfs",
        required=False,
        default=False,
        action="store_true",
        help="Dont discard ORFs. Default: False",
    )
    filter_parser.add_argument(
        "--debug",
        required=False,
        default=False,
        action="store_true",
        help="Enable TRACE level in file log, and DEBUG on StreamHandler."
        "Default: False (DEBUG level on file and INFO on console)",
    )
    filter_parser.add_argument(
        "--workers",
        required=False,
        default=0,
        type=int,
        help="Number of workers to use. Default: max_workers in ProcessPoolExecutor",
    )
    filter_parser.add_argument(
        "--gff-suffix",
        required=False,
        default=".gff3",
        type=str,
        help="Suffix for GFF files. Default: .gff3",
    )
    filter_parser.add_argument(
        "--query-string",
        required=False,
        default=gff3_utils.QS_GENE_TRNA_RRNA,
        type=str,
        help="Pandas query string to filter GFF3 files. "
        """Default: 'type == ["gene", "tRNA", "rRNA"]'""",
    )

    # TODO create a query string for filtering

    write_parser = subparsers.add_parser("write", help="Write GDT to file")
    write_parser.add_argument("--gdt", required=True, help="GDT file to write")
    write_parser.add_argument("--out", required=True, help="Output file to write")
    write_parser.add_argument(
        "--debug",
        required=False,
        default=False,
        action="store_true",
        help="Enable TRACE level in file log. Default: False (DEBUG level)",
    )

    stripped_parser = subparsers.add_parser(
        "stripped", help="Create a stripped GDT version of a GDT file"
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
    stripped_parser.add_argument(
        "--debug",
        required=False,
        default=False,
        action="store_true",
        help="Enable TRACE level in file log. Default: False (DEBUG level)",
    )

    test_parser = subparsers.add_parser("test", help="Test command")
    test_parser.add_argument(
        "--debug",
        required=False,
        default=False,
        action="store_true",
        help="Enable TRACE level in file log. Default: False (DEBUG level)",
    )

    args = parser.parse_args()

    if args.debug:
        log_path, log = logger_setup.logger_creater(
            console_level="DEBUG", file_level="TRACE"
        )
        log.trace("TRACE level enabled in file log.")
    else:
        log_path, log = logger_setup.logger_creater(
            console_level="INFO", file_level="DEBUG"
        )

    log.info(
        f"Logging to console and file. Check logfile for more details. ({log_path})"
    )
    log.debug("CLI run called.")
    log.debug(f"exec path: {Path().resolve()}")
    log.debug(f"cli  path: {Path(__file__)}")
    log.debug(f"args: {args}")

    if args.command == "filter":
        args.tsv = Path(args.tsv).resolve()

        if args.gdt:
            args.gdt = Path(args.gdt).resolve()

        log.debug("Filter command called.")
        tsv_filter.filter_whole_tsv(
            log,
            args.tsv,
            args.gdt,
            args.orfs,
            args.workers,
            args.AN_column,
            args.gff_suffix,
            args.query_string,
        )

    elif args.command == "write":
        log.debug("Write command")
        gd = gene_dict_impl.create_gene_dict(args.gdt, max_an_sources=0)
        gene_dict_impl.write_gdt_file(gd, args.out, overwrite=True)

    elif args.command == "test":
        log.debug("Test command")
        pass

    elif args.command == "stripped":
        log.debug("Stripped command")
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
