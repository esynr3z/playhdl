import pkg_resources
import os
from typing import Dict, Callable, Dict
from pathlib import Path
from enum import Enum
import json
import distutils
from contextlib import contextmanager


from . import log

_logger = log.get_logger()


def get_pkg_version() -> str:
    """Get version of the package"""
    return pkg_resources.get_distribution("playhdl").version


def is_debug_en() -> bool:
    """Is debug enabled"""
    return "DEBUG" in os.environ


class ExtendedJsonEncoder(json.JSONEncoder):
    """Custom encoder that can serialize more types"""

    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, Enum):
            return obj.name
        else:
            return json.JSONEncoder.default(self, obj)


def dump_json(file: Path, data: Dict):
    """Dump data to a JSON file"""
    with file.open("w") as f:
        json.dump(data, f, cls=ExtendedJsonEncoder, indent=4)


def load_json(file: Path) -> Dict:
    """Load data from a JSON file"""
    with file.open("r") as f:
        return json.load(f)


@contextmanager
def query_if_file_exists(filepath: Path, force_yes: bool = False):
    if filepath.is_file():
        # Provide message and lamda with dump method in case caller want to query user for further steps
        _logger.warning(f"File '{filepath}' already exists. It will be overwriten!")
        if force_yes or input_query_yes_no():
            yield
    else:
        yield


def input_query_yes_no(question: str = "Do you want to proceed?") -> bool:
    """Ask a yes/no question"""
    _logger.warning(f"{question} [y/n]")
    while True:
        try:
            return distutils.util.strtobool(input().lower())  # type: ignore
        except ValueError:
            _logger.error("Usupported answer! Please type y/yes or n/no.")


class ExtendedEnum(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        """This uses enumeration name as a string value for auto() call"""
        return name.lower()

    def __str__(self):
        return self.value

    @classmethod
    def aslist(cls):
        """List of values of the enum"""
        return list(map(lambda c: c.value, cls))
