from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from typing import Any, Dict, TYPE_CHECKING

from . import log, tools, utils

if TYPE_CHECKING:
    from pathlib import Path

_logger = log.get_logger()


@dataclass
class UserSettings:
    tools: Dict[tools.ToolUid, tools.ToolSettings] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        for uid, settings in self.tools.items():
            # dataclass can't handle nesting, so deserealization has to be done mannualy
            if isinstance(settings, dict):
                self.tools[uid] = tools.ToolSettings(**settings)


def setup(app_dir: Path, user_settings_file: Path, **kwargs: Any) -> None:
    """Create settings and application folder for a first time"""
    # Prepare application directory
    _logger.info(f"Create application home ...'{app_dir}'")
    app_dir.mkdir(parents=True, exist_ok=True)

    # Prepare settings file
    _logger.info("Create default settings ...")
    _logger.info("  Try to find all tools available ...")
    tool_pool = {}
    for t in tools.ToolKind:
        bin_dir = tools.find_tool_dir(t)
        _logger.info(f"  {t}: {bin_dir}")
        if bin_dir:
            tool_pool[str(t)] = tools.ToolSettings(kind=t, bin_dir=bin_dir)
    user_settings = UserSettings(tools=tool_pool)

    # Try to save settings to file
    _logger.info(f"Save settings to '{user_settings_file}' ...")
    if utils.is_write_allowed(user_settings_file, bool(kwargs.get("query_force_yes", False))):
        dump(user_settings_file, user_settings)


def dump(file: Path, settings: UserSettings) -> None:
    """Dump user settings to file"""
    utils.dump_json(file, dataclasses.asdict(settings))
    _logger.info(f"Settings were successfuly dumped to '{file}'")


def load(file: Path) -> UserSettings:
    """Load user settings from file"""
    data = utils.load_json(file)
    settings = UserSettings(**data)
    _logger.debug(f"Loaded user settings: {settings}")
    _logger.info(f"Settings were successfuly loaded from '{file}'")
    return settings
