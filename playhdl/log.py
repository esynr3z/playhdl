import logging

from . import utils


class CustomFormatter(logging.Formatter):
    """Formatter based on https://stackoverflow.com/a/56944256"""

    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_s = "%(levelname)s: %(message)s"

    formats = {
        logging.DEBUG: green + format_s + reset,
        logging.INFO: grey + format_s + reset,
        logging.WARNING: yellow + format_s + reset,
        logging.ERROR: red + format_s + reset,
        logging.CRITICAL: bold_red + format_s + reset,
    }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger: logging.Logger


def init_logger():
    """Initialize global logger"""
    global logger

    # Create logger
    logger = logging.getLogger("playhdl")
    logger.setLevel(logging.DEBUG)

    # Create console handler with custom formatting
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if utils.is_debug_en() else logging.INFO)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)


def debug(*args, **kwargs) -> None:
    logger.debug(*args, **kwargs)


def info(*args, **kwargs) -> None:
    logger.info(*args, **kwargs)


def warning(*args, **kwargs) -> None:
    logger.warning(*args, **kwargs)


def error(*args, **kwargs) -> None:
    logger.error(*args, **kwargs)
