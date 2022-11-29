from __future__ import annotations
from typing import Literal, Dict, List, Callable, NoReturn, Optional, Union, Type
from pathlib import Path
from enum import Enum
import subprocess
import io
from dataclasses import dataclass, field

import pydantic
import toml

from . import utils
from . import log

ToolKind = Literal[
    "modelsim",
    "xcelium",
    "verilator",
    "icarus",
    "vcs",
    "vivado",
]

DesignMode = Literal[
    "verilog",
    "systemverilog",
    "vhdl",
]

LibraryKind = Literal[
    "none",
    "uvm12",
]


@dataclass
class ToolDescriptor:
    kind: ToolKind
    bin_dir: Path
    repr_str: str


ToolPool = Dict[str, ToolDescriptor]


@dataclass
class UserSettings:
    tools: ToolPool = field(default_factory=dict)


class GlobalSettings:
    app_dir = Path.home().joinpath(".playhdl")
    settings_file = app_dir.joinpath("settings.ini")

    def __init__(self) -> None:
        self.user_settings: UserSettings

    def setup(self) -> None:
        """Create settings for a first time"""
        # Prepare application directory
        log.debug(f"Try to create application home '{self.app_dir}'")
        self.app_dir.mkdir(parents=True, exist_ok=True)

        # Prepare settings file
        if self.settings_file.is_file():
            raise FileExistsError(f"Settings file '{self.settings_file}' exists already")
        else:
            log.debug(f"Try to create settings file '{self.settings_file}' and fill with defaults")
            raise NotImplementedError

    def _auto_find_tools(self) -> ToolPool:
        """Try to automatically find all avalaible tools"""
        raise NotImplementedError
