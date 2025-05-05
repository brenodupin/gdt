# -*- coding: utf-8 -*-

import logging
import datetime
from pathlib import Path
import os, glob
from typing import Optional

def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(logging.TRACE):
        self._log(logging.TRACE, message, args, **kwargs)

# Add the method to the Logger class
logging.TRACE = 5
logging.addLevelName(logging.TRACE, 'TRACE')
logging.Logger.trace = trace

_logging_levels = {'CRITICAL': logging.CRITICAL,
                   'ERROR': logging.ERROR,
                   'WARNING': logging.WARNING,
                   'INFO': logging.INFO,
                   'DEBUG': logging.DEBUG,
                   'TRACE': logging.TRACE}

def cleanup_logs(log_dir: Path, max_files: int = 10):
    log_files = sorted(glob.glob(str(log_dir / "gdt_*.log")))
    for old_file in log_files[:-(max_files-1)]:
        try:
            os.remove(old_file)
        except Exception as e:
            print(f"Error removing old log file {old_file}: {e}")
            raise

def logger_setup(console_level: Optional[str] = None, file_level: Optional[str] = None) -> tuple[str, logging.Logger]:
    """Set up the logger for the GDT package.
    Args:
        console_level (Optional[str]): Logging level for console output. Defaults to INFO.
        file_level (Optional[str]): Logging level for file output. Defaults to DEBUG.
    Returns:
        tuple[str, logging.Logger]: Tuple containing the log file path and the logger instance.
    """
    
    console_level = _logging_levels.get(console_level, logging.INFO)
    file_level = _logging_levels.get(file_level, logging.DEBUG)

    package_dir = Path(__file__).parent
    log_dir = package_dir / 'logs'
    
    log_dir.mkdir(exist_ok=True)
    
    # Create a timestamp-based log filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H_%M_%S")
    log_file_path = log_dir / f"gdt_{timestamp}.log"
    
    # Clean up old log files (keep only the 5 most recent)
    cleanup_logs(log_dir)

    # Create and configure logger
    logger = logging.getLogger('gdt')
    logger.setLevel(logging.TRACE)
    
    # Remove any existing handlers (in case logger was already configured)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    logger.propagate = False
    
    logger.debug(f'Logger setup complete. Logging to {log_file_path}')
    return log_file_path, logger