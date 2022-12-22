"""Tests for playhdl/cli.py
"""

import shutil
from dataclasses import dataclass

from pathlib import Path  # noqa: TC003
from typing import Dict

import playhdl.cli as cli
import playhdl.project as project
import playhdl.settings as settings
import pytest

from .utils import OverrideSysArgv, shell


@pytest.fixture
def project_descr(project_data: Dict) -> project.Project:
    return project.Project(**project_data)


def test_run_as_module():
    result = shell("python -m playhdl --help")
    assert result.returncode == 1


def test_entrypoint():
    result = shell("playhdl")
    assert result.returncode == 2
    assert "usage:" in result.stderr


@pytest.mark.parametrize("args", ["-h", "init -h", "setup -h", "run -h", "info -h"])
def test_usage(args: str):
    result = shell(f"playhdl {args}")
    assert result.returncode == 0


@dataclass
class AppPaths:
    app_dir: Path
    user_settings_file: Path
    project_file: Path
    project_dir: Path


@pytest.fixture
def app_paths(tmp_path: Path) -> AppPaths:
    cli.app_dir = tmp_path.joinpath(".playhdl")
    cli.user_settings_file = cli.app_dir.joinpath("settings.json")
    cli.project_file = tmp_path.joinpath("playhdl.json")
    return AppPaths(
        app_dir=cli.app_dir,
        user_settings_file=cli.user_settings_file,
        project_file=cli.project_file,
        project_dir=tmp_path,
    )


@pytest.fixture(autouse=True)
def change_test_dir(app_paths: AppPaths, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(app_paths.project_dir)


@pytest.mark.skipif(not shutil.which("iverilog"), reason="requires icarus verilog")
def test_flow(app_paths: AppPaths):
    with OverrideSysArgv("playhdl", "setup"):
        cli.main()
        assert app_paths.user_settings_file.is_file() is True
    with OverrideSysArgv("playhdl", "init", "verilog"):
        cli.main()
        assert app_paths.project_file.is_file() is True
    with OverrideSysArgv("playhdl", "run", "icarus"):
        cli.main()
        assert app_paths.project_dir.joinpath("icarus").joinpath("tb.vcd").is_file()


def test_not_found_settings(app_paths: AppPaths, caplog: pytest.LogCaptureFixture):
    with OverrideSysArgv("playhdl", "init", "sv"):
        with pytest.raises(SystemExit):
            cli.main()
        assert "ERROR" in caplog.text
        assert "Settings file" in caplog.text
        assert "was not found" in caplog.text


def test_not_found_project(app_paths: AppPaths, user_settings: settings.UserSettings, caplog: pytest.LogCaptureFixture):
    app_paths.app_dir.mkdir()
    settings.dump(app_paths.user_settings_file, user_settings)
    with OverrideSysArgv("playhdl", "run", "icarus"):
        with pytest.raises(SystemExit):
            cli.main()
        assert "ERROR" in caplog.text
        assert "Project file" in caplog.text
        assert "was not found" in caplog.text


def test_run_no_args(
    app_paths: AppPaths,
    user_settings: settings.UserSettings,
    project_descr: project.Project,
    caplog: pytest.LogCaptureFixture,
):
    app_paths.app_dir.mkdir()
    settings.dump(app_paths.user_settings_file, user_settings)
    project.dump(app_paths.project_file, project_descr)
    with OverrideSysArgv("playhdl", "run"):
        with pytest.raises(SystemExit):
            cli.main()
        assert "You can run simulation" in caplog.text


def test_init_no_args(
    app_paths: AppPaths,
    user_settings: settings.UserSettings,
    caplog: pytest.LogCaptureFixture,
):
    app_paths.app_dir.mkdir()
    settings.dump(app_paths.user_settings_file, user_settings)
    with OverrideSysArgv("playhdl", "init"):
        with pytest.raises(SystemExit):
            cli.main()
        assert "You can initialize project" in caplog.text


def test_run_wrong_tool(
    app_paths: AppPaths,
    user_settings: settings.UserSettings,
    project_descr: project.Project,
    caplog: pytest.LogCaptureFixture,
):
    app_paths.app_dir.mkdir()
    settings.dump(app_paths.user_settings_file, user_settings)
    project.dump(app_paths.project_file, project_descr)
    with OverrideSysArgv("playhdl", "run", "foobar"):
        with pytest.raises(SystemExit):
            cli.main()
        assert "foobar" in caplog.text
        assert "was not found in your project file" in caplog.text


def test_init_no_suitable_tool(
    app_paths: AppPaths,
    user_settings: settings.UserSettings,
    caplog: pytest.LogCaptureFixture,
):
    app_paths.app_dir.mkdir()
    user_settings.tools.pop("vivado")
    user_settings.tools.pop("vcs2020")
    settings.dump(app_paths.user_settings_file, user_settings)
    with OverrideSysArgv("playhdl", "init", "sv_uvm12"):
        with pytest.raises(SystemExit):
            cli.main()
        assert "Can't find any suitable tool" in caplog.text


def test_info(
    app_paths: AppPaths,
    user_settings: settings.UserSettings,
    caplog: pytest.LogCaptureFixture,
):
    app_paths.app_dir.mkdir()
    settings.dump(app_paths.user_settings_file, user_settings)
    with OverrideSysArgv("playhdl", "info"):
        cli.main()
        assert "Tools available" in caplog.text
        assert "Tools compatibility table" in caplog.text
