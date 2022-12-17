"""Tests for playhdl/templates/__init__.py
"""

from io import StringIO
from pathlib import Path

import playhdl.tools as tools

import pytest

from playhdl.settings import dump, load, setup, UserSettings


class TestSetup:
    @pytest.fixture
    def app_dir(self, tmp_path: Path) -> Path:
        return tmp_path.joinpath("home/.app")

    @pytest.fixture
    def settings_file(self, app_dir: Path) -> Path:
        return app_dir.joinpath("settings.json")

    def _read_file(self, file: Path) -> str:
        with file.open("r") as f:
            return f.read()

    def _write_file(self, file: Path, text: str) -> None:
        with file.open("w") as f:
            f.write(text)

    def test_smoke(self, app_dir: Path, settings_file: Path):
        setup(app_dir, settings_file)
        assert app_dir.is_dir() is True
        assert settings_file.is_file() is True
        assert self._read_file(settings_file) != ""

    def test_dir_exists(self, app_dir: Path, settings_file: Path):
        app_dir.mkdir(parents=True)
        setup(app_dir, settings_file)

    def test_file_exists_overwrite(self, app_dir: Path, settings_file: Path, monkeypatch: pytest.MonkeyPatch):
        app_dir.mkdir(parents=True)
        some_text = "The answer is 42"
        self._write_file(settings_file, some_text)

        monkeypatch.setattr("sys.stdin", StringIO("a\nc\ny"))
        setup(app_dir, settings_file)
        assert self._read_file(settings_file) != some_text

    def test_file_exists_no_overwrite(self, app_dir: Path, settings_file: Path, monkeypatch: pytest.MonkeyPatch):
        app_dir.mkdir(parents=True)
        some_text = "The answer is 42"
        self._write_file(settings_file, some_text)

        monkeypatch.setattr("sys.stdin", StringIO("a\nc\nn"))
        setup(app_dir, settings_file)
        assert self._read_file(settings_file) == some_text

    def test_file_exists_force_overwrite(self, app_dir: Path, settings_file: Path, monkeypatch: pytest.MonkeyPatch):
        app_dir.mkdir(parents=True)
        some_text = "The answer is 42"
        self._write_file(settings_file, some_text)

        monkeypatch.setattr("sys.stdin", StringIO("a\nc\nn"))
        setup(app_dir, settings_file, query_force_yes=True)
        assert self._read_file(settings_file) != some_text

    def test_dump_load(self, app_dir: Path, settings_file: Path):
        app_dir.mkdir(parents=True)
        test_settings = UserSettings(
            **{
                "tools": {
                    "modelsim20": tools.ToolSettings(tools.ToolKind.MODELSIM, Path("/home/modelsim"), {}, {}),
                    "verilator5": tools.ToolSettings(
                        tools.ToolKind.VERILATOR, Path("/home/verilator5"), {"FOO": "1"}, {"BAR": True}
                    ),
                }
            }
        )
        dump(settings_file, test_settings)
        settings = load(settings_file)
        assert settings == test_settings

    def test_setup_load(self, app_dir: Path, settings_file: Path):
        setup(app_dir, settings_file, query_force_yes=True)
        settings = load(settings_file)
        assert isinstance(settings, UserSettings)
