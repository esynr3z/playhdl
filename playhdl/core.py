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


@dataclass
class UserSettings:
    tools: Dict[str, ToolDescriptor] = field(default_factory=dict)


class _Core:
    app_home = Path.home().joinpath(".playhdl")
    app_settings = app_home.joinpath("settings.ini")

    def __init__(self) -> None:
        self._user_settings: UserSettings

    def setup(self) -> None:
        # Prepare home directory
        log.debug(f"Try to create application home '{self.app_home}'")
        self.app_home.mkdir(parents=True, exist_ok=True)

        # Prepare global settings
        if self.app_settings.is_file():
            self._load_global_settings()
        else:
            log.debug(f"Global settings '{APP_SETTINGS}' was not found. Create and fill with defaults.'")
            self._user_settings = UserSettings(**{})
            self._save_global_settings()
        log.debug("Global settings are:", self.global_settings)

    def die(self, msg: Optional[Union[str, int]] = 1) -> NoReturn:
        exit(msg)

    @property
    def global_settings(self) -> UserSettings:
        """Global settings for the application"""
        return self._user_settings

    def _load_global_settings(self):
        """Load global settings from a file"""
        log.debug(f"Load global settings from a file '{APP_SETTINGS}'")
        try:
            self._user_settings = UserSettings.from_toml(APP_SETTINGS)
        except pydantic.ValidationError as e:
            log.error(f"Validation of {APP_SETTINGS} failed!")
            self.die(str(e))

    def _save_global_settings(self):
        """Save global settings to a file"""
        log.debug(f"Save global settings to a file '{APP_SETTINGS}'")
        self._user_settings.to_toml(APP_SETTINGS)

    def open_code_editor(self, project_dir: Path) -> None:
        """Open project in the code editor"""
        CodeEditorKind.get_cls(self.global_settings.code_editor).open_project(project_dir)

    def open_settings(self) -> None:
        """Open settings"""
        CodeEditorKind.get_cls(self.global_settings.code_editor).open_file(APP_SETTINGS)


core = _Core()
