from __future__ import annotations
from pathlib import Path
from typing import List
import dataclasses
from dataclasses import dataclass

from . import log
from . import templates
from . import settings
from . import tools
from . import utils


def init(
    session_file: Path,
    design_kind: templates.DesignKind,
    sources: List[str],
    user_settings: settings.UserSettings,
):
    available_tools = set(t.kind for t in user_settings.tools.values())

    # Generate simulator scripts for the selected design mode
    tool_scripts = {}
    for t in available_tools:
        try:
            tool_scripts[t] = tools.generate_script(t, design_kind, sources)
        except ValueError:
            pass
    if len(tool_scripts) == 0:
        raise ValueError(f"Can't find any suitable tool for the provided design mode '{design_kind}'")

    # Filter scripts according available tools
    pass
