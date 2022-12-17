"""Tests for playhdl/project.py
"""

from copy import deepcopy
from io import StringIO
from pathlib import Path
from typing import Dict

import playhdl.settings as settings

import playhdl.templates as templates
import playhdl.tools as tools
import pytest
from playhdl.project import create, dump, load, Project


@pytest.fixture
def project_data() -> Dict:
    return {
        "tools": {
            "modelsim20": {"build": ["foo", "bar"], "sim": ["baz"], "waves": []},
            "verilator5": {"build": [], "sim": [], "waves": []},
        }
    }


@pytest.fixture
def project_file(tmp_path: Path) -> Path:
    return tmp_path.joinpath("playhdl.json")


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


def test_project_deserealization(project_data: Dict):
    proj = Project(**project_data)
    assert isinstance(proj.tools["modelsim20"], tools.ToolScript)
    assert isinstance(proj.tools["verilator5"], tools.ToolScript)


def test_create_verilog(project_file: Path, user_settings: settings.UserSettings):
    proj = create(project_file, templates.DesignKind.verilog, ["tb.v"], user_settings)
    assert len(proj.tools) == 4


def test_create_sv(project_file: Path, user_settings: settings.UserSettings):
    proj = create(project_file, templates.DesignKind.sv, ["tb.sv"], user_settings)
    assert len(proj.tools) == 4


def test_create_sv_uvm12(project_file: Path, user_settings: settings.UserSettings):
    proj = create(project_file, templates.DesignKind.sv_uvm12, ["tb.sv"], user_settings)
    assert len(proj.tools) == 2
    assert set(list(proj.tools.keys())) == set(["vivado", "vcs2020"])


def test_create_vhdl(project_file: Path, user_settings: settings.UserSettings):
    with pytest.raises(ValueError):
        create(project_file, templates.DesignKind.vhdl, ["tb.vhd"], user_settings)


def test_dump_load(project_file: Path, project_data: Dict):
    proj = Project(**project_data)
    dump(project_file, proj)
    loaded_proj = load(project_file)
    assert proj == loaded_proj


def test_dump_exists_overwrite(project_file: Path, project_data: Dict, monkeypatch):
    orig_proj = Project(**project_data)
    dump(project_file, orig_proj)

    new_proj = deepcopy(orig_proj)
    new_proj.tools.pop("verilator5")

    monkeypatch.setattr("sys.stdin", StringIO("a\nc\ny"))
    dump(project_file, new_proj)
    assert new_proj == load(project_file)


def test_dump_exists_no_overwrite(project_file: Path, project_data: Dict, monkeypatch):
    orig_proj = Project(**project_data)
    dump(project_file, orig_proj)

    new_proj = deepcopy(orig_proj)
    new_proj.tools.pop("verilator5")

    monkeypatch.setattr("sys.stdin", StringIO("a\nc\nn"))
    dump(project_file, new_proj)
    assert orig_proj == load(project_file)


def test_dump_exists_force_overwrite(project_file: Path, project_data: Dict, monkeypatch):
    orig_proj = Project(**project_data)
    dump(project_file, orig_proj)

    new_proj = deepcopy(orig_proj)
    new_proj.tools.pop("verilator5")

    monkeypatch.setattr("sys.stdin", StringIO("a\nc\nn"))
    dump(project_file, new_proj, query_force_yes=True)
    assert new_proj == load(project_file)
