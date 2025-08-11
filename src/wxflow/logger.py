"""
Logger
"""

import logging
import os
import sys
from functools import wraps
from pathlib import Path
from typing import Union

__all__ = ['Logger', 'logit', 'setup_logging', 'add_stream_logger', 'add_file_logger']

DEFAULT_FORMAT = '%(asctime)s - %(levelname)-8s - %(name)-12s: %(message)s'


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
    def __init__(self, name: str = None,
                 level: str = os.environ.get("LOGGING_LEVEL", "INFO"),
                 _format: str = DEFAULT_FORMAT,
                 colored_log: bool = False,
                 stdout: bool = True,
                 logfile_path: Union[str, Path] = None):
        """
        Initialize Logger

        Parameters
        ----------
        name         : str
                       Name of the Logger object
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
                       Enable logging to stdout
                       default : True
        logfile_path : str or Path
                       Path for logging to a file
                       default : None
        """

        self.name = name
        self.level = level
        self._format = _format
        self.colored_log = colored_log
        self.stdout = stdout
        self.logfile_path = logfile_path

        setup_logging(level=self.level,
                      _format=self._format,
                      colored_log=self.colored_log,
                      stdout=self.stdout,
                      logfile_path=self.logfile_path)

        self._logger = logging.getLogger(name) if name else logging.getLogger()

        return

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


def add_stream_logger(logger: logging.Logger,
                      level: str = 'INFO',
                      _format: str = DEFAULT_FORMAT,
                      colored_log: bool = False):
    """
    Log to stdout
    This method will allow setting a custom stream handler on the logger

    Parameters
    ----------
    logger : logging.Logger
             Logger object to add a new handler to
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
    handler.setLevel(level)
    _format = ColoredFormatter(
        _format) if colored_log else logging.Formatter(_format)
    handler.setFormatter(_format)
    logger.addHandler(handler)


def add_file_logger(logger: logging.Logger,
                    logfile_path: Union[str, Path],
                    level: str = os.environ.get("LOGGING_LEVEL", "INFO"),
                    _format: str = DEFAULT_FORMAT):
    """
    Log to a file
    This method will allow setting custom file handler on the logger

    Parameters
    ----------
    logger : logging.Logger
             Logger object to add a new handler to
    logfile_path: str or Path
                  Path for writing out logfiles from logging
                  default : None
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
    handler.setLevel(level)
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


def setup_logging(level: str = os.environ.get("LOGGING_LEVEL", "INFO"),
                  _format: str = DEFAULT_FORMAT,
                  colored_log: bool = False,
                  stdout: bool = True,
                  logfile_path: Union[str, Path] = None):
    """
    Setup logging with the given parameters.

    Parameters
    ----------
    level        : str
                   Logging level
                   default : 'INFO'
    _format      : str
                   Logging format
                   default : '%(asctime)s - %(levelname)-8s - %(name)-12s: %(message)s'
    colored_log  : bool
                   Use colored logging for stdout
                   default: False
    stdout       : bool
                   Enable logging to stdout
                   default : True
    logfile_path : str or Path
                   Path for logging to a file
                   default : None

    Returns
    -------
    logger : Logger object
             Configured logger instance.
    """

    LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    print(f"Inputs: {level=}, {_format=}, {colored_log=}, {stdout=}, {logfile_path=}")

    _level = level.upper()
    _ilevel = getattr(logging, _level, logging.INFO)
    print(f"Will set up logging with {level=}, {_level=}, {_ilevel=}")

    if _level not in LOG_LEVELS:
        raise LookupError(f"{level} is unknown logging level\n" +
                              f"Currently supported log levels are:\n" +
                              f"{' | '.join(LOG_LEVELS)}")

    logger = logging.getLogger()

    # Remove all existing handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)

    logging.basicConfig(level=_ilevel, format=_format)
    #logger = logging.getLogger()
    print("Logger initialized with level:", logger.level)

    # Add console handler for logger
    if stdout:
        add_stream_logger(logger, level=_level, _format=_format, colored_log=colored_log)

    # Add file handler for logger
    if logfile_path is not None:
        add_file_logger(logger, logfile_path, level=_level, _format=format)
