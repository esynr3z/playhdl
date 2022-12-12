"""Tests for playhdl/log.py
"""

from playhdl.log import *


def test_log():
    init_logger()
    logger = get_logger()
    logger.info("The")
    logger.warning("answer")
    logger.error("is")
    logger.critical("42")
