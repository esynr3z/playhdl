import pkg_resources
import os
from typing import Dict, Tuple, Any, List
from pathlib import Path
from enum import Enum
import json
import distutils
import sys
import inspect

from . import log


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


def json_dump(file: Path, data: Dict):
    """Dump data to a JSON file"""
    with file.open("w") as f:
        json.dump(data, f, cls=ExtendedJsonEncoder, indent=4)


def get_module_sublcasses(module_name: str, subclass: type) -> List[type]:
    """Get all subclasses in the module"""
    found = []
    for name, cls in inspect.getmembers(sys.modules[module_name], inspect.isclass):
        if issubclass(cls, subclass):
            found.append(cls)
    return found


def input_query_yes_no(question: str = "Do you want to proceed?") -> bool:
    """Ask a yes/no question"""
    log.warning(f"{question} [y/n]")
    while True:
        try:
            return distutils.util.strtobool(input().lower())
        except ValueError:
            log.error("Usupported answer! Please type y/yes or n/no.")


class ExtendedEnum(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        """This uses enumeration name as a string value for auto() call"""
        return name

    def __str__(self):
        return self.value

    @classmethod
    def aslist(cls):
        """List of values of the enum"""
        return list(map(lambda c: c.value, cls))
