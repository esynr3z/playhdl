"""Tests for playhdl/tools.py
"""

import pytest
from io import StringIO
import shutil

from playhdl.tools import *
from playhdl.tools import _Tool
import playhdl.templates as templates


def _get_base_exe_name(tool_kind: ToolKind) -> str:
    return {
        ToolKind.ICARUS: "iverilog",
        ToolKind.MODELSIM: "vsim",
        ToolKind.VCS: "vcs",
        ToolKind.XCELIUM: "xmsim",
        ToolKind.VIVADO: "xsim",
        ToolKind.VERILATOR: "verilator",
    }[tool_kind]


@pytest.mark.parametrize("tool_kind", ToolKind.aslist())
def test_find_tool_dir(tool_kind):
    bin_path = shutil.which(_get_base_exe_name(tool_kind))
    expected = Path(bin_path).parent if bin_path else None
    assert find_tool_dir(tool_kind) == expected


def test_get_compatibility_text_table():
    table = get_compatibility_text_table()
    for k in ToolKind:
        assert str(k) in table
    for k in templates.DesignKind:
        assert str(k) in table
