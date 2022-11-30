from __future__ import annotations
from pathlib import Path
import dataclasses
from dataclasses import dataclass

from . import log
from . import tools
from . import utils


@dataclass
class UserSettings:
    tools: tools.ToolPool = dataclasses.field(default_factory=dict)


def setup_user(app_dir: Path, user_settings_file: Path) -> None:
    """Create settings and application folder for a first time"""
    # Prepare application directory
    log.info(f"Create application home ...'{app_dir}'")
    app_dir.mkdir(parents=True, exist_ok=True)

    # Prepare settings file
    log.info(f"Create settings file ...")
    log.info(f"  Try to find all tools available ...")
    tool_pool = {}
    for t in tools.ToolKind:
        bin_dir = tools.find_tool_dir(t)
        log.info(f"  {t}: {bin_dir}")
        if bin_dir:
            tool_pool[t] = tools.ToolDescriptor(kind=t, bin_dir=bin_dir)
    user_settings = UserSettings(tools=tool_pool)

    log.info(f"Save settings file to '{user_settings_file}' ...")
    if user_settings_file.is_file():
        log.warning(f"Settings file '{user_settings_file}' already exists. It will be overwriten!")
    dump_user_settings(user_settings_file, user_settings)
    log.info(f"Done!")


def dump_user_settings(file: Path, settings: UserSettings) -> None:
    """Dump user settings to file"""
    utils.json_dump(file, dataclasses.asdict(settings))
