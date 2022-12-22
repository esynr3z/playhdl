from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from typing import Any, Dict, List, TYPE_CHECKING

from . import log, tools, utils

if TYPE_CHECKING:
    from pathlib import Path

    from . import settings, templates

_logger = log.get_logger()


@dataclass
class Project:
    tools: Dict[tools.ToolUid, tools.ToolScript] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        for uid, script in self.tools.items():
            # dataclass can't handle nesting, so deserealization has to be done mannualy
            if isinstance(script, dict):
                self.tools[uid] = tools.ToolScript(**script)


def create(
    project_file: Path,
    design_kind: templates.DesignKind,
    sources: List[str],
    user_settings: settings.UserSettings,
) -> Project:
    project_tools: Dict[tools.ToolUid, tools.ToolScript] = {}

    for uid, tool_settings in user_settings.tools.items():
        try:
            project_tools[uid] = tools.generate_script(tool_settings, design_kind, sources)
        except (KeyError, ValueError, NotImplementedError):
            pass

    if len(list(project_tools.keys())) == 0:
        raise ValueError(f"Can't find any suitable tool for the provided design mode '{design_kind}'")

    project = Project(tools=project_tools)
    _logger.debug(f"Created project: {project}")

    return project


def dump(file: Path, project: Project, **kwargs: Any) -> None:
    """Dump project to file"""
    if utils.is_write_allowed(file, bool(kwargs.get("query_force_yes", False))):
        utils.dump_json(file, dataclasses.asdict(project))
    _logger.info(f"Project was successfuly saved to '{file}'")


def load(file: Path) -> Project:
    """Load project from file"""
    data = utils.load_json(file)
    project = Project(**data)
    _logger.debug(f"Loaded project: {project}")
    _logger.info(f"Project was successfuly loaded from '{file}'")
    return project
