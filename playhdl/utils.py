import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Union

import pkg_resources

from . import log

_logger = log.get_logger()


def get_pkg_version() -> str:
    """Get version of the package"""
    return pkg_resources.get_distribution("playhdl").version


class ExtendedJsonEncoder(json.JSONEncoder):
    """Custom encoder that can serialize more types"""

    def default(self, obj: Any) -> Union[str, Any]:
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, Enum):
            return obj.name
        else:
            return json.JSONEncoder.default(self, obj)


def dump_json(file: Path, data: Dict) -> None:
    """Dump data to a JSON file"""
    with file.open("w") as f:
        json.dump(data, f, cls=ExtendedJsonEncoder, indent=4)


def load_json(file: Path) -> Dict:
    """Load data from a JSON file"""
    with file.open("r") as f:
        return json.load(f)


def is_write_allowed(filepath: Path, force_yes: bool = False) -> bool:
    """Query user if file exists and write it then"""
    if filepath.is_file():
        # Provide message and lamda with dump method in case caller want to query user for further steps
        _logger.warning(f"File '{filepath}' already exists. It will be overwriten!")
        return force_yes or input_query_yes_no()
    else:
        return True


def input_query_yes_no(question: str = "Do you want to proceed?") -> bool:
    """Ask a yes/no question"""
    _logger.warning(f"{question} [y/n]")
    while True:
        try:
            return {"y": True, "n": False}[input().lower()]
        except KeyError:
            _logger.error("Usupported answer! Please type y/yes or n/no.")


class ExtendedEnum(str, Enum):
    def _generate_next_value_(name, start: int, count: int, last_values: List[Any]) -> Any:  # type: ignore
        """This uses enumeration name as a string value for auto() call"""
        return name.lower()

    def __str__(self) -> str:
        return self.value

    @classmethod
    def aslist(cls) -> List[str]:
        """List of values of the enum"""
        return list(map(lambda c: c.value, cls))  # type: ignore
