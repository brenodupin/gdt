# -*- coding: utf-8 -*-

import logging
import datetime
from pathlib import Path
import os
import glob
from typing import Any, Optional, cast

TRACE = 5


class GDTLogger(logging.Logger):
    def trace(self, message: Any, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(TRACE):
            self._log(TRACE, message, args, **kwargs)


logging.addLevelName(TRACE, "TRACE")
logging.setLoggerClass(GDTLogger)

_logging_levels: dict[str, int] = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "TRACE": TRACE,
}


def cleanup_logs(log_dir: Path, max_files: int = 10) -> None:
    log_files = sorted(glob.glob(str(log_dir / "gdt_*.log")))
    for old_file in log_files[: -(max_files - 1)]:
        try:
            os.remove(old_file)
        except Exception as e:
            print(f"Error removing old log file {old_file}: {e}")
            raise


def logger_creater(
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    log_file: Optional[Path] = None,
) -> tuple[Path, GDTLogger]:
    """Set up the logger for the GDT package.
    Args:
        console_level (Optional[str]): Log level for console output. Defaults to INFO.
        file_level (Optional[str]): Log level for file output. Defaults to DEBUG.
    Returns:
        tuple[str, logging.Logger]: Tuple with log file path and the logger instance.
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

    log.debug(f"Logger setup complete. Logging to {log_file_path}")
    return log_file_path, log
