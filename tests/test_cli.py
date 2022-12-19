"""Tests for playhdl/cli.py
"""

from dataclasses import dataclass
from pathlib import Path

from utils import OverrideSysArgv, shell
import playhdl.cli as cli
import pytest


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


def test_setup(app_paths: AppPaths):
    with OverrideSysArgv("playhdl", "setup"):
        cli.main()
        assert app_paths.user_settings_file.is_file() is True
