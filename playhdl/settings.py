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

    def __post_init__(self):
        for uid, descriptor in self.tools.items():
            # dataclass can't handle nesting, so deserealization has to be done mannualy
            # 'descriptor' here is raw dict after original init, so type checker is wrong
            self.tools[uid] = tools.ToolDescriptor(**descriptor)  # type: ignore


def setup_user(app_dir: Path, user_settings_file: Path) -> None:
    """Create settings and application folder for a first time"""
    # Prepare application directory
    log.info(f"Create application home ...'{app_dir}'")
    app_dir.mkdir(parents=True, exist_ok=True)

    # Prepare settings file
    log.info(f"Create default settings ...")
    log.info(f"  Try to find all tools available ...")
    tool_pool = {}
    for t in tools.ToolKind:
        bin_dir = tools.find_tool_dir(t)
        log.info(f"  {t}: {bin_dir}")
        if bin_dir:
            tool_pool[t] = tools.ToolDescriptor(kind=t, bin_dir=bin_dir)
    user_settings = UserSettings(tools=tool_pool)

    # Try to save settings to file
    log.info(f"Save settings to '{user_settings_file}' ...")
    utils.write_file_aware_existance(
        user_settings_file,
        lambda: dump_user_settings(user_settings_file, user_settings),
    )


def dump_user_settings(file: Path, settings: UserSettings) -> None:
    """Dump user settings to file"""
    utils.dump_json(file, dataclasses.asdict(settings))
    log.info(f"Settings are successfuly dumped to '{file}'")


def load_user_settings(file: Path) -> UserSettings:
    """Load user settings from file"""
    data = utils.load_json(file)
    settings = UserSettings(**data)
    log.debug(f"Loaded user settings: {settings}")
    log.info(f"Settings are successfuly loaded from '{file}'")
    return settings
