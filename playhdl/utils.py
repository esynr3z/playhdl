from __future__ import annotations
import pkg_resources
import os
from typing import TypeVar
from pathlib import Path

import toml
import pydantic


def get_pkg_version() -> str:
    """Get version of the package"""
    return pkg_resources.get_distribution("playhdl").version


def is_debug_en() -> bool:
    """Is debug enabled"""
    return "DEBUG" in os.environ


_T = TypeVar("_T", bound="BaseModel")


class BaseModel(pydantic.BaseModel):
    """Custom pydantic BaseModel"""

    class Config:
        anystr_strip_whitespace = True
        validate_all = True
        extra = pydantic.Extra.forbid
        use_enum_values = True
        allow_mutation = False

    def to_toml(self, file: Path) -> None:
        """Dump settings to a TOML file."""
        with file.open("w") as toml_file:
            toml.dump(self.dict(), toml_file, toml.TomlPathlibEncoder())

    @classmethod
    def from_toml(cls, file: Path) -> _T:
        with file.open("r") as toml_file:
            return cls(**toml.load(toml_file))
