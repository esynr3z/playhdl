from __future__ import annotations
from typing import Any, Dict
from pathlib import Path
import dataclasses
from dataclasses import dataclass

from . import log
from . import tools
from . import utils

logger = log.get_logger()


@dataclass
class ToolSettings:
    kind: tools.ToolKind
    bin_dir: Path
    env: Dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclass
class UserSettings:
    tools: Dict[tools.ToolUid, ToolSettings] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        for uid, settings in self.tools.items():
            # dataclass can't handle nesting, so deserealization has to be done mannualy
            if isinstance(settings, dict):
                self.tools[uid] = ToolSettings(**settings)


def setup_user(app_dir: Path, user_settings_file: Path) -> None:
    """Create settings and application folder for a first time"""
    # Prepare application directory
    logger.info(f"Create application home ...'{app_dir}'")
    app_dir.mkdir(parents=True, exist_ok=True)

    # Prepare settings file
    logger.info(f"Create default settings ...")
    logger.info(f"  Try to find all tools available ...")
    tool_pool = {}
    for t in tools.ToolKind:
        bin_dir = tools.find_tool_dir(t)
        logger.info(f"  {t}: {bin_dir}")
        if bin_dir:
            tool_pool[t] = ToolSettings(kind=t, bin_dir=bin_dir)
    user_settings = UserSettings(tools=tool_pool)

    # Try to save settings to file
    logger.info(f"Save settings to '{user_settings_file}' ...")
    utils.write_file_aware_existance(
        user_settings_file,
        lambda: dump(user_settings_file, user_settings),
    )


def dump(file: Path, settings: UserSettings) -> None:
    """Dump user settings to file"""
    utils.dump_json(file, dataclasses.asdict(settings))
    logger.info(f"Settings were successfuly dumped to '{file}'")


def load(file: Path) -> UserSettings:
    """Load user settings from file"""
    data = utils.load_json(file)
    settings = UserSettings(**data)
    logger.debug(f"Loaded user settings: {settings}")
    logger.info(f"Settings were successfuly loaded from '{file}'")
    return settings
