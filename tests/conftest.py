from pathlib import Path
from typing import Dict

import playhdl.settings as settings
import playhdl.tools as tools
import pytest


@pytest.fixture
def project_data() -> Dict:
    return {
        "tools": {
            "modelsim20": {"build": ["foo", "bar"], "sim": ["baz"], "waves": []},
            "verilator5": {"build": [], "sim": [], "waves": []},
        }
    }


@pytest.fixture
def user_settings() -> settings.UserSettings:
    return settings.UserSettings(
        **{
            "tools": {
                "modelsim20": tools.ToolSettings(tools.ToolKind.MODELSIM, Path("/home/modelsim"), {}, {}),
                "verilator5": tools.ToolSettings(tools.ToolKind.VERILATOR, Path("/home/verilator5"), {}, {}),
                "vcs2020": tools.ToolSettings(tools.ToolKind.VCS, Path("/home/vcs"), {}, {}),
                "vivado": tools.ToolSettings(tools.ToolKind.VIVADO, Path("/home/vivado"), {}, {}),
            }
        }
    )
