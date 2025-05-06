# -*- coding: utf-8 -*-

import gdt.logger_setup
import gdt.gene_dict
import gdt.gff3_utils
import gdt.tsv_filter

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
    filter_parser.add_argument("--debug", required=False, default=False, action="store_true", help="Enable TRACE level in file log, and DEBUG on StreamHandler. Default: False (DEBUG level on file and INFO on console)")
    filter_parser.add_argument("--workers", required=False, default=0, type=int, help="Number of workers to use. Default: max_workers in ProcessPoolExecutor")
    
    write_parser = subparsers.add_parser('write', help='Write GDT to file')
    write_parser.add_argument('--gdt', required=True, help='GDT file to write')
    write_parser.add_argument('--out', required=True, help='Output file to write')
    write_parser.add_argument("--debug", required=False, default=False, action="store_true", help="Enable TRACE level in file log. Default: False (DEBUG level)")

    
    args = parser.parse_args()
    
    if args.debug:
        log_path, logger = gdt.logger_setup.logger_creater(console_level='DEBUG', file_level='TRACE')
        logger.trace("TRACE level enabled in file log.")
    else:
        log_path, logger = gdt.logger_setup.logger_creater(console_level='INFO', file_level='DEBUG')

    logger.info(f"Logging to console and file. Check logfile for more details. ({log_path})")
    logger.debug('CLI run called.')
    logger.debug(f'exec path: {Path().resolve()}')
    logger.debug(f'cli  path: {Path(__file__)}')
    logger.debug(f'args: {args}')

    if args.command == 'filter':
        args.tsv = Path(args.tsv).resolve()
        
        if args.gdt:
            args.gdt = Path(args.gdt).resolve()
        
        logger.debug('Filter command called.')
        a = gdt.tsv_filter.filter_whole_tsv(logger, args.tsv, args.gdt, args.orfs, args.workers, args.AN_column)
    
    elif args.command == 'write':
        logger.debug("Write command")
        gd = gdt.gene_dict.create_gene_dict(args.gdt, max_an_sources=0)
        a = gdt.gene_dict.write_gdt_file(gd, args.out, overwrite=True)