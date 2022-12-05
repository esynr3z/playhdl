from __future__ import annotations
from pathlib import Path
from typing import List, Dict
import dataclasses
from dataclasses import dataclass

from . import log
from . import templates
from . import settings
from . import tools
from . import utils

_logger = log.get_logger()


@dataclass
class Project:
    tools: Dict[tools.ToolUid, tools.ToolScript] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        for uid, script in self.tools.items():
            # dataclass can't handle nesting, so deserealization has to be done mannualy
            if isinstance(script, dict):
                self.tools[uid] = tools.ToolScript(**script)


def init(
    project_file: Path,
    design_kind: templates.DesignKind,
    sources: List[str],
    user_settings: settings.UserSettings,
):
    available_tools = set(t.kind for t in user_settings.tools.values())
    _logger.debug(f"Available tools according user settings: {available_tools}")

    # Generate simulator scripts for the selected design mode
    tool_scripts: Dict[tools.ToolKind, tools.ToolScript] = {}
    for t in available_tools:
        try:
            tool_scripts[t] = tools.generate_script(t, design_kind, sources)
        except (ValueError, NotImplementedError):
            pass
    if len(tool_scripts) == 0:
        raise ValueError(f"Can't find any suitable tool for the provided design mode '{design_kind}'")
    _logger.debug(f"Generated tool scripts for '{design_kind}': {list(tool_scripts.keys())}")

    # Create project descriptor
    project_tools: Dict[tools.ToolUid, tools.ToolScript] = {}
    for uid, settings in user_settings.tools.items():
        try:
            project_tools[uid] = tool_scripts[settings.kind]
        except KeyError:
            pass
    project = Project(tools=project_tools)
    _logger.debug(f"Created project: {project}")

    # Dump project file
    _logger.info(f"Save project file to '{project_file}' ...")
    utils.write_file_aware_existance(
        project_file,
        lambda: dump(project_file, project),
    )


def dump(file: Path, project: Project) -> None:
    """Dump project to file"""
    utils.dump_json(file, dataclasses.asdict(project))
    _logger.info(f"Project was successfuly saved to '{file}'")


def load(file: Path) -> Project:
    """Load project from file"""
    data = utils.load_json(file)
    project = Project(**data)
    _logger.debug(f"Loaded project: {project}")
    _logger.info(f"Project was successfuly loaded from '{file}'")
    return project
