# -*- coding: utf-8 -*-
"""Logger setup and management for GDT (Gene Dict Tool).

This module provides functionality to create and configure loggers for the GDT
package, including support for a custom TRACE logging level.

The logger can be configured to output logs to the console and/or to a file,
with customizable logging levels.

Newer version of this file is a backport of the tigre logger, which is used in tigre.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from . import gdict

TRACE = 5

_RawMsg = tuple[int, str]


class TempLogger:
    """Temporary logger to buffer log messages.

    This logger buffers messages in memory and can be used to collect logs
    during a specific operation, such as cleaning GFF files. It supports
    logging at various levels, including a custom TRACE level.

    This approach is thread-safe and allows for easy collection of log records
    without writing to a file or console immediately.
    """

    __slots__ = ("buffer", "trace_enable")

    def __init__(self, trace_enable: bool = False) -> None:
        """Initialize the buffered logger."""
        self.buffer: list[_RawMsg] = []
        self.trace_enable = trace_enable

    def _log(self, level: int, msg: str) -> None:
        """Log a message at the specified level."""
        self.buffer.append((level, msg))

    def error(self, msg: str) -> None:
        """Log an error message."""
        self._log(logging.ERROR, msg)

    def warning(self, msg: str) -> None:
        """Log a warning message."""
        self._log(logging.WARNING, msg)

    def info(self, msg: str) -> None:
        """Log an info message."""
        self._log(logging.INFO, msg)

    def debug(self, msg: str) -> None:
        """Log a debug message."""
        self._log(logging.DEBUG, msg)

    def trace(self, msg: str) -> None:
        """Log a trace message."""
        if self.trace_enable:
            self._log(TRACE, msg)

    def get_records(self) -> list[_RawMsg]:
        """Return the list of log records."""
        return self.buffer.copy()

    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer.clear()


class GDTLogger(logging.Logger):
    """Extended logger class for GDT with TRACE (5) level support."""

    def __init__(self, name: str, level: int = logging.NOTSET) -> None:
        """Initialize the GDT logger with custom TRACE level."""
        super().__init__(name, level)
        self._trace_enabled = self.level <= TRACE

    def setLevel(self, level: int | str) -> None:  # noqa: N802
        """Override setLevel to update cached trace status."""
        super().setLevel(level)
        self._trace_enabled = self.level <= TRACE

    def trace(self, message: Any, *args: Any, **kwargs: Any) -> None:
        """Log 'msg % args' with severity 'TRACE'.

        Trace is a custom level below DEBUG (10), but above NOTSET (0), valued at 5.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.trace("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        if self.isEnabledFor(TRACE):
            self._log(TRACE, message, args, **kwargs)

    def spawn_buffer(self) -> TempLogger:
        """Create a buffered logger to collect log records."""
        return TempLogger(self._trace_enabled)


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


def create_logger(
    print_to_console: bool = True,
    console_level: str = "INFO",
    save_to_file: bool = True,
    file_level: str = "DEBUG",
    log_file: Path | str | None = None,
) -> GDTLogger:
    """Create a logger with optional console and file output.

    Args:
        print_to_console (bool): Whether to print logs to console. Defaults to True.
        console_level (str): Log level for console output.
        save_to_file (bool): Whether to save logs to a file.
        file_level (str): Log level for file output.
        log_file (Path | str | None): Path to the log file.

    Returns:
        GDTLogger: Configured logger instance.

    """
    log = cast(GDTLogger, logging.getLogger("gdt"))
    levels = []
    # Remove any existing handlers
    for handler in log.handlers[:]:
        log.removeHandler(handler)

    if print_to_console:
        console_level_int = _logging_levels.get(console_level, logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level_int)
        console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        log.addHandler(console_handler)
        levels.append(console_level_int)

    if save_to_file:
        assert log_file is not None, "log_file must be provided if save_to_file is True"
        log_file = Path(log_file).resolve()
        log_file.touch(exist_ok=True)

        file_level_int = _logging_levels.get(file_level, logging.DEBUG)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(file_level_int)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        log.addHandler(file_handler)
        levels.append(file_level_int)

    log.setLevel(min(levels) if levels else _logging_levels["DISABLE"])
    log.propagate = False
    log.debug("Logger initialized.")
    log.debug(f"Console logging level {console_level if print_to_console else 'None'}")
    if save_to_file:
        log.debug(f"File logging level {file_level} at {log_file}")

    return log


def setup_logger(
    verbose: int,
    log_file: Path | str | None,
    quiet: bool,
    no_log_file: bool,
    cmd: str,
) -> GDTLogger:
    """Set up logger based on command line arguments.

    Verbosity levels:
    0 (default): INFO console,  DEBUG file
    1 (-v):      INFO console,  TRACE file
    2 (-vv):     DEBUG console, TRACE file
    3 (-vvv):    TRACE console, TRACE file
    """
    # Determine console level based on verbosity
    if quiet:
        console_level = "DISABLE"
    elif verbose <= 1:
        console_level = "INFO"
    elif verbose == 2:
        console_level = "DEBUG"
    elif verbose >= 3:
        console_level = "TRACE"

    # Determine file level based on verbosity
    if no_log_file:
        file_level = "DISABLE"
    elif verbose == 0:
        file_level = "DEBUG"
    elif verbose >= 1:
        file_level = "TRACE"

    if log_file:  # `--log` provided, ensure it's a Path
        log_file = Path(log_file).resolve()

    # default behavior, both `--log` and `--no-log-file` not provided
    elif not no_log_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = Path(f"gdt_{cmd}_{timestamp}.log").resolve()

    else:  # `--no-log-file` provided
        log_file = None

    log = create_logger(
        print_to_console=not quiet,
        console_level=console_level,
        save_to_file=not no_log_file,
        file_level=file_level,
        log_file=log_file,
    )

    return log


def log_info(
    log: GDTLogger,
    gd: "gdict.GeneDict",
    *,
    spacer: str = "\t",
    method: str | None = None,
) -> None:
    """Log information about the GeneDict object.

    Args:
        log (GDTLogger): Logger instance to use for logging.
        gd (GeneDict): GeneDict object containing the information to log.
        spacer (str): String to prepend to each log message for formatting.
                      Defaults to tab.
        method (str | None): Name of the logging method to use, e.g., 'debug',
                                'info', etc. Defaults to 'info'.

    """
    log_func = getattr(log, method) if method else log.info
    log_func(f"{spacer}Labels: {gd.info.labels}")
    log_func(f"{spacer}Total Entries   : {gd.info.total_entries}")
    log_func(f"{spacer}GeneDescriptions: {gd.info.gene_descriptions}")
    log_func(f"{spacer}GeneGenerics    : {gd.info.gene_generics}")
    log_func(f"{spacer}DbxrefGeneIDs   : {gd.info.dbxref_GeneIDs}")
