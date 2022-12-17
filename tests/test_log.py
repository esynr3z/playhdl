"""Tests for playhdl/log.py
"""
import os

from playhdl.log import get_logger, init_logger, is_debug_en


def test_is_debug_en():
    os.environ.setdefault("DEBUG", "1")
    assert is_debug_en() is True
    os.environ.pop("DEBUG")
    assert is_debug_en() is False


def test_log():
    init_logger()
    logger = get_logger()
    logger.info("The")
    logger.warning("answer")
    logger.error("is")
    logger.critical("42")
