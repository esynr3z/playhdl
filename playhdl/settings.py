from __future__ import annotations
import typing
from typing import Literal, Dict
from pathlib import Path
import dataclasses
from dataclasses import dataclass
import json

from . import log
from . import tools
from . import utils


@dataclass
class UserSettings:
    tools: tools.ToolPool = dataclasses.field(default_factory=dict)


def setup_user(app_dir: Path, user_settings_file: Path, force: bool = False) -> None:
    """Create settings and application folder for a first time"""
    # Prepare application directory
    log.debug(f"Try to create application home '{app_dir}'")
    app_dir.mkdir(parents=True, exist_ok=True)

    # Prepare settings file
    if user_settings_file.is_file() and not force:
        raise FileExistsError(f"Settings file '{user_settings_file}' already exists!")
    log.debug(f"Try to create settings file '{user_settings_file}' and fill with defaults")
    tool_pool = {}
    for t in typing.get_args(tools.ToolKind):
        tool_pool[f"{t}_unique_id_can_be_here"] = tools.ToolDescriptor(kind=t, bin_dir=Path("/path/to/bin/dir"))
    user_settings = UserSettings(tools=tool_pool)
    dump_user_settings(user_settings_file, user_settings)


def dump_user_settings(file: Path, settings: UserSettings) -> None:
    """Dump user settings to file"""
    utils.json_dump(file, dataclasses.asdict(settings))
