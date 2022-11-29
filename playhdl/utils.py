from __future__ import annotations
import pkg_resources
import os
from typing import Dict
from pathlib import Path
import json


def get_pkg_version() -> str:
    """Get version of the package"""
    return pkg_resources.get_distribution("playhdl").version


def is_debug_en() -> bool:
    """Is debug enabled"""
    return "DEBUG" in os.environ


class PathJsonEncoder(json.JSONEncoder):
    """Custom encoder that can serialize pathlib paths"""

    def default(self, o):
        if isinstance(o, Path):
            return str(o)
        else:
            return o


def json_dump(file: Path, data: Dict):
    """Dump data to a JSON file"""
    with file.open("w") as f:
        json.dump(data, f, cls=PathJsonEncoder, indent=4)


def input_query_yes_no(question: str) -> bool:
    """Ask a yes/no question"""
    print(f"{question} [y/n]")
    while True:
        answer = input().lower()
        if answer.startswith("y"):
            return True
        elif answer.startswith("n"):
            return False
        else:
            print("Usupported answer! Please type y/yes or n/no.")
