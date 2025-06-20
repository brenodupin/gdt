# -*- coding: utf-8 -*-
"""Logger setup and management for GDT (Gene Dict Tool).

This module provides functionality to create and configure loggers for the GDT
package, including support for a custom TRACE logging level.

The logger can be configured to output logs to the console and/or to a file,
with customizable logging levels.
"""

import datetime
import glob
import logging
import os
from pathlib import Path
from typing import Any, Optional, Union, cast

from . import gdt_impl

TRACE = 5


class GDTLogger(logging.Logger):
    """Extended logger class for GDT with TRACE (5) level support."""

    def trace(self, message: Any, *args: Any, **kwargs: Any) -> None:
        """Log 'msg % args' with severity 'TRACE'.

        Trace is a custom level below DEBUG, but above INFO, valued at 5.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.trace("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        if self.isEnabledFor(TRACE):
            self._log(TRACE, message, args, **kwargs)


logging.addLevelName(TRACE, "TRACE")
logging.setLoggerClass(GDTLogger)

_logging_levels: dict[str, int] = {
    "DISABLE": logging.CRITICAL + 1,  # above CRITICAL, used to disable logging
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "TRACE": TRACE,
    "NOTSET": logging.NOTSET,
}


def cleanup_logs(log_dir: Path, max_files: int = 10) -> None:
    """Remove old log files, keeping only the most recent ones.

    Args:
        log_dir (Path): Directory where log files are stored.
        max_files (int): Maximum number of log files to keep. Defaults to 10.

    """
    log_files = sorted(glob.glob(str(log_dir / "gdt_*.log")))
    for old_file in log_files[: -(max_files - 1)]:
        try:
            os.remove(old_file)
        except Exception as e:
            print(f"Error removing old log file {old_file}: {e}")
            raise


def create_dev_logger(
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    log_file: Optional[Path] = None,
) -> GDTLogger:
    """Set up the logger for the GDT package.

    Args:
        console_level (str): Logging level for console output.
        file_level (str): Logging level for file output.
        log_file (Optional[Path]): Path to the log file. If None, a default
                                   log file will be created at the project root,

    Returns:
        GDTLogger: Configured logger instance.

    """
    console_level_int = _logging_levels.get(console_level, logging.INFO)
    file_level_int = _logging_levels.get(file_level, logging.DEBUG)

    if log_file:
        log_file_path = Path(log_file).resolve()
        log_file_path.touch(exist_ok=True)

    else:
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"

        log_dir.mkdir(exist_ok=True)

        # Create a timestamp-based log filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")
        log_file_path = log_dir / f"gdt_{timestamp}.log"
        cleanup_logs(log_dir)

    # Create and configure logger
    log = cast(GDTLogger, logging.getLogger("gdt"))
    log.setLevel(TRACE)

    # Remove any existing handlers (in case logger was already configured)
    for handler in log.handlers[:]:
        log.removeHandler(handler)

    # Create console handler
    # (StreamHandler defaults to sys.stderr, can be changed to sys.stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level_int)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    log.addHandler(console_handler)

    # Create file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(file_level_int)
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    log.addHandler(file_handler)

    log.propagate = False

    log.debug("Dev log setup complete")
    log.debug(f"Console logging level {console_level}")
    log.debug(f"File logging level {file_level} at {log_file_path}")
    return log


def create_simple_logger(
    print_to_console: bool = True,
    console_level: str = "INFO",
    save_to_file: bool = True,
    file_level: str = "DEBUG",
    log_file: Union[Path, str, None] = None,
) -> GDTLogger:
    """Create a simple logger with optional console and file output.

    Args:
        print_to_console (bool): Whether to print logs to console. Defaults to True.
        console_level (Optional[str]): Log level for console output.
        save_to_file (bool): Whether to save logs to a file.
        file_level (Optional[str]): Log level for file output.
        log_file (Optional[Path]): Path to the log file.

    Returns:
        GDTLogger: Configured logger instance.

    """
    log = cast(GDTLogger, logging.getLogger("gdt"))
    log.setLevel(TRACE)
    # Remove any existing handlers
    for handler in log.handlers[:]:
        log.removeHandler(handler)

    if print_to_console:
        console_level_int = _logging_levels.get(console_level, logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level_int)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        log.addHandler(console_handler)

    if save_to_file:
        if log_file is None:
            print(
                "No log file specified, even though save_to_file is True. "
                "Log will be save in the current directory in 'gdt_default.log'."
            )
            log_file = "gdt_default.log"

        log_file_path = Path(log_file).resolve()
        log_file_path.touch(exist_ok=True)

        file_level_int = _logging_levels.get(file_level, logging.DEBUG)
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(file_level_int)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        log.addHandler(file_handler)

    log.propagate = False
    log.debug("Simple log setup complete.")
    log.debug(f"Console logging level {console_level if print_to_console else 'None'}")
    log.debug(
        f"File logging level {file_level} at {log_file_path if log_file else 'None'}"
    )

    return log


def setup_logger(
    debug: bool, log_file: Union[Path, str, None], quiet: bool
) -> GDTLogger:
    """Set up logger based on command line arguments."""
    console_level = "DISABLE" if quiet else ("DEBUG" if debug else "INFO")
    file_level = "TRACE" if debug else "DEBUG"

    # Create logger based on log file preference
    if log_file:
        log_file = Path(log_file).resolve()
        log = create_simple_logger(
            print_to_console=not quiet,
            console_level=console_level,
            file_level=file_level,
            log_file=log_file,
        )
    else:
        log = create_dev_logger(console_level=console_level, file_level=file_level)

    log.trace("Logger setup complete.")
    return log


def log_gdt_info(
    log: GDTLogger,
    gdt: gdt_impl.GeneDict,
    spacer: str = "\t",
    method: Optional[str] = None,
) -> None:
    """Log information about the GeneDict object.

    Args:
        log (GDTLogger): Logger instance to use for logging.
        gdt (GeneDict): GeneDict object containing the information to log.
        spacer (str): String to prepend to each log message for formatting.
                      Defaults to tab.
        method (Optional[str]): Name of the logging method to use, e.g., 'debug',
                                'info', etc. Defaults to 'info'.

    """
    log_func = getattr(log, method) if method else log.info
    log_func(f"{spacer}Labels: {gdt.info.labels}")
    log_func(f"{spacer}Total Entries   : {gdt.info.total_entries}")
    log_func(f"{spacer}GeneDescriptions: {gdt.info.gene_descriptions}")
    log_func(f"{spacer}GeneGenerics    : {gdt.info.gene_generics}")
    log_func(f"{spacer}DbxrefGeneIDs   : {gdt.info.dbxref_GeneIDs}")
