"""Tests for playhdl/runner.py
"""

from pathlib import Path

import playhdl.project as project
import playhdl.settings as settings
import playhdl.tools as tools

import pytest
from playhdl.runner import run


@pytest.fixture
def project_descr() -> project.Project:
    data = {
        "tools": {
            "modelsim20": {"build": ["touch build.log"], "sim": ["touch sim.log"], "waves": ["touch waves.log"]},
        }
    }
    return project.Project(**data)  # type: ignore


@pytest.fixture
def user_settings() -> settings.UserSettings:
    return settings.UserSettings(
        **{
            "tools": {
                "modelsim20": tools.ToolSettings(tools.ToolKind.MODELSIM, Path("/home/modelsim"), {}, {}),
            }
        }
    )


def test_run(project_descr: project.Project, user_settings: settings.UserSettings):
    tool_uid = "modelsim20"
    run(project_descr, user_settings, tool_uid, True)
    assert Path(f"{tool_uid}/build.log").is_file() is True
    assert Path(f"{tool_uid}/sim.log").is_file() is True
    assert Path(f"{tool_uid}/waves.log").is_file() is True


def test_run_no_waves(project_descr: project.Project, user_settings: settings.UserSettings):
    tool_uid = "modelsim20"
    run(project_descr, user_settings, tool_uid, False)
    assert Path(f"{tool_uid}/build.log").is_file() is True
    assert Path(f"{tool_uid}/sim.log").is_file() is True
    assert Path(f"{tool_uid}/waves.log").is_file() is False


def test_run_wrong_uid(project_descr: project.Project, user_settings: settings.UserSettings):
    tool_uid = "modelsim42"
    with pytest.raises(ValueError):
        run(project_descr, user_settings, tool_uid, False)


def test_run_empty_cmd(
    project_descr: project.Project,
    user_settings: settings.UserSettings,
    caplog: pytest.LogCaptureFixture,
):
    tool_uid = "modelsim20"
    project_descr.tools[tool_uid].build = [""]
    run(project_descr, user_settings, tool_uid, False)
    assert Path(f"{tool_uid}/build.log").is_file() is False
    assert "WARNING" in caplog.text


def test_run_err_cmd(project_descr: project.Project, user_settings: settings.UserSettings):
    tool_uid = "modelsim20"
    project_descr.tools[tool_uid].build = ["ls /foobar"]
    with pytest.raises(RuntimeError):
        run(project_descr, user_settings, tool_uid, False)
