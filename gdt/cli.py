# -*- coding: utf-8 -*-

from gdt.logger_setup import logger_setup
from gdt.tsv_filter import filter_whole_tsv
from pathlib import Path
import argparse

def cli_run():
    """Test function for CLI."""
    # TODO pick a better description
    parser = argparse.ArgumentParser(description='Gene Dictionary Tool (GDT) command line interface')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    subparsers.required = True

    # TODO pick a better description
    filter_parser = subparsers.add_parser('filter', help='Filter tsv ans into AN_missing_dbxref or AN_missing_gene_dict')
    filter_parser.add_argument('--tsv',   required=True,  help='TSV file to filter')
    filter_parser.add_argument('--AN-column', required=False, default='AN', type=str, help='Column name for NCBI Accession Number. Default: AN')
    filter_parser.add_argument('--gdt',   required=False, default=False, help='GDT filed that will be used as base')
    filter_parser.add_argument("--orfs",  required=False, default=False, action="store_true", help="Dont discard ORFs. Default: False")
    filter_parser.add_argument("--debug", required=False, default=False, action="store_true", help="Enable TRACE level in file log. Default: False (DEBUG level)")
    filter_parser.add_argument("--workers", required=False, default=0, type=int, help="Number of workers to use. Default: max_workers in ProcessPoolExecutor")
    args = parser.parse_args()
    

    if args.command == 'filter':
        console_level = 'DEBUG'
        if args.debug:
            log_path, logger = logger_setup(console_level=console_level, file_level='TRACE')
            logger.trace("TRACE level enabled in file log.")
        else:
            log_path, logger = logger_setup(console_level=console_level, file_level='DEBUG')

        logger.info(f"Logging to console and file. Check logfile for more details. ({log_path})")
        logger.debug('CLI run called.')
        logger.debug(f'exec path: {Path().resolve()}')
        logger.debug(f'cli  path: {Path(__file__)}')
        
        args.tsv = Path(args.tsv).resolve()
        if args.gdt:
            args.gdt = Path(args.gdt).resolve()
        
        logger.debug(f'args: {args}')
        logger.debug('Filter command called.')
        a = filter_whole_tsv(logger, args.tsv, args.gdt, args.orfs, args.workers, args.AN_column)

        

        
        

