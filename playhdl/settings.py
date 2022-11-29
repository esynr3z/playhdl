from __future__ import annotations
import typing
from typing import Literal, Dict
from pathlib import Path
import dataclasses
from dataclasses import dataclass
import json

from . import log
from . import tools


@dataclass
class UserSettings:
    tools: tools.ToolPool = dataclasses.field(default_factory=dict)


class Settings:
    app_dir = Path.home().joinpath(".playhdl")
    user_settings_file = app_dir.joinpath("settings.json")

    def __init__(self) -> None:
        self.user_settings: UserSettings

    def setup(self) -> None:
        """Create settings for a first time"""
        # Prepare application directory
        log.debug(f"Try to create application home '{self.app_dir}'")
        self.app_dir.mkdir(parents=True, exist_ok=True)

        # Prepare settings file
        if self.user_settings_file.is_file():
            raise FileExistsError(f"Settings file '{self.user_settings_file}' exists already")
        else:
            log.debug(f"Try to create settings file '{self.user_settings_file}' and fill with defaults")

            tool_pool = {}
            for t in typing.get_args(tools.ToolKind):
                tool_pool[f"{t}_unique_id_can_be_here"] = tools.ToolDescriptor(kind=t, bin_dir=Path("/path/to/bin/dir"))
            self.user_settings = UserSettings(tools=tool_pool)
            self.dump_user_settings()

    def dump_user_settings(self) -> None:
        """Dump user settings to file"""
        with open(self.user_settings_file, "w") as f:
            json.dump(dataclasses.asdict(self.user_settings), f)

    def _auto_find_tools(self) -> tools.ToolPool:
        """Try to automatically find all avalaible tools"""
        raise NotImplementedError
