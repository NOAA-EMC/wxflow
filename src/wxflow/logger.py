"""
Logger
"""

import logging
import os
import sys
from functools import wraps
from pathlib import Path
from typing import Union

__all__ = ['Logger', 'add_stream_logger', 'add_file_logger', 'logit']


class ColoredFormatter(logging.Formatter):
    """
    Logging colored formatter
    adapted from https://stackoverflow.com/a/56944256/3638629
    """

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.formats = {
            logging.DEBUG: self.blue + self.fmt + self.reset,
            logging.INFO: self.grey + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger:
    """
    Improved logging
    """
    LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    DEFAULT_LEVEL = 'INFO'
    DEFAULT_FORMAT = '%(asctime)s - %(levelname)-8s - %(name)-12s: %(message)s'

    def __init__(self, name: str = None,
                 level: str = os.environ.get("LOGGING_LEVEL"),
                 _format: str = DEFAULT_FORMAT,
                 colored_log: bool = False,
                 stdout: bool = True,
                 logfile_path: Union[str, Path] = None):
        """
        Initialize Logger

        Parameters
        ----------
        name         : str
                       Name of the Logger object (None implies root logger)
                       default : None
        level        : str
                       Desired Logging level
                       default : 'INFO'
        _format      : str
                       Desired Logging Format
                       default : '%(asctime)s - %(levelname)-8s - %(name)-12s: %(message)s'
        colored_log  : bool
                       Use colored logging for stdout
                       default: False
        stdout       : bool
                       Stream to stdout
                       default: False
        logfile_path : str or Path
                       Path for logging to a file
                       default : None
        """

        self.name = name if name else 'root'
        self.level = level.upper() if level else Logger.DEFAULT_LEVEL
        self.format = _format
        self.colored_log = colored_log
        self.stdout = stdout
        self.logfile_path = logfile_path

        if self.level not in Logger.LOG_LEVELS:
            raise LookupError(f"{level} (case insensitive) is unknown logging level\n" +
                              f"Currently supported log levels are:\n" +
                              f"{' | '.join(Logger.LOG_LEVELS)}")

        # Initialize the root logger
        self._root_logger = logging.getLogger()

        # Initialize logger if no name is present
        self._logger = logging.getLogger(name) if name else self._root_logger

        # If a name is provided, set the parent logger to the root logger
        self._parent_logger = self._logger.parent if name else self._root_logger

        self._logger.setLevel(self.level)

        # Disable propagation to avoid duplicate logs in parent loggers
        self._logger.propagate = False

        # Remove all existing handlers attached to this logger
        for _handler in self._logger.handlers:
            self._logger.removeHandler(_handler)

        # Stream to stdout
        if self.stdout:
            add_stream_logger(self._logger, level=self.level, _format=self.format, colored_log=self.colored_log)

        # Stream to file
        if self.logfile_path is not None:
            add_file_logger(self._logger, self.logfile_path, level=self.level, _format=self.format)

    def __getattr__(self, attribute):
        """
        Allows calling logging module methods directly

        Parameters
        ----------
        attribute : str
                    attribute name of a logging object

        Returns
        -------
        attribute : logging attribute
        """
        return getattr(self._logger, attribute)

    def get_logger(self):
        """
        Return the logging object

        Returns
        -------
        logger : Logger object
        """
        return self._logger


def add_stream_logger(logger: Logger,
                      level: str = Logger.DEFAULT_LEVEL,
                      _format: str = Logger.DEFAULT_FORMAT,
                      colored_log: bool = False):
    """
    Stream logs to stdout
    This method will allow setting a custom stream handler on children

    Parameters
    ----------
    logger : logging.Logger
             Logger object to which the stream handler will be added
    level : str
            logging level
            default : 'INFO'
    _format : str
                logging format
                default : '%(asctime)s - %(levelname)-8s - %(name)-12s: %(message)s'
    colored_log : bool
                    enable colored output for stdout
                    default : False

    Returns
    -------
    None
    """

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level.upper())
    _format = ColoredFormatter(
        _format) if colored_log else logging.Formatter(_format)
    handler.setFormatter(_format)
    logger.addHandler(handler)


def add_file_logger(logger: logging.Logger,
                    logfile_path: Union[str, Path],
                    level: str = Logger.DEFAULT_LEVEL,
                    _format: str = Logger.DEFAULT_FORMAT):
    """
    Stream output to a logfile
    This method will allow setting custom file handler on children
    Create stream handler

    Parameters
    ----------
    logger : logging.Logger
             Logger object to which the file handler will be added
    logfile_path: str or Path
                    Path for writing out logfiles from logging
                    default : False
    level : str
            logging level
            default : 'INFO'
    _format : str
                logging format
                default : '%(asctime)s - %(levelname)-8s - %(name)-12s: %(message)s'

    Returns
    -------
    None
    """

    logfile_path = Path(logfile_path)

    # Create the directory containing the logfile_path
    if not logfile_path.parent.is_dir():
        logfile_path.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(str(logfile_path))
    handler.setLevel(level.upper())
    handler.setFormatter(logging.Formatter(_format))
    logger.addHandler(handler)


def logit(logger, name=None, message=None):
    """
    Logger decorator to add logging to a function.
    Simply add:
    @logit(logger) before any function
    Parameters
    ----------
    logger  : Logger
              Logger object
    name    : str
              Name of the module to be logged
              default: __module__
    message : str
              Name of the function to be logged
              default: __name__
    """

    def decorate(func):

        log_name = name if name else func.__module__
        log_msg = message if message else log_name + "." + func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):

            passed_args = [repr(aa) for aa in args]
            passed_kwargs = [f"{kk}={repr(vv)}" for kk, vv in list(kwargs.items())]

            call_msg = 'BEGIN: ' + log_msg
            logger.info(call_msg)
            logger.debug(f"( {', '.join(passed_args + passed_kwargs)} )")

            # Call the function
            retval = func(*args, **kwargs)

            # Close the logging with printing the return val
            ret_msg = '  END: ' + log_msg
            logger.info(ret_msg)
            logger.debug(f" returning: {retval}")

            return retval

        return wrapper

    return decorate
