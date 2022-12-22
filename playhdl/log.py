import logging
import os


class _CustomFormatter(logging.Formatter):
    """Formatter based on https://stackoverflow.com/a/56944256"""

    grey = "\x1b[38;20m"
    cyan = "\x1b[34;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    generic_format = "[%(name)s][%(levelname)s] %(message)s"
    debug_format = "[%(name)s][%(levelname)s][%(filename)s:%(lineno)d] %(message)s"

    formats = {
        logging.DEBUG: green + debug_format + reset,
        logging.INFO: cyan + generic_format + reset,
        logging.WARNING: yellow + generic_format + reset,
        logging.ERROR: red + generic_format + reset,
        logging.CRITICAL: bold_red + generic_format + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def is_debug_en() -> bool:
    """Is debug enabled"""
    return "DEBUG" in os.environ


def init_logger() -> None:
    """Initialize global logger"""
    # Create logger
    logger = logging.getLogger("playhdl")
    logger.setLevel(logging.DEBUG)

    # Create console handler with custom formatting
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if is_debug_en() else logging.INFO)
    ch.setFormatter(_CustomFormatter())
    logger.addHandler(ch)


def get_logger() -> logging.Logger:
    """Get package logger"""
    return logging.getLogger("playhdl")
