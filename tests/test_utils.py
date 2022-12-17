"""Tests for playhdl/utils.py
"""

import enum
from enum import Enum
from io import StringIO
from pathlib import Path

import playhdl
import playhdl.utils as utils
import pytest


def test_get_pkg_version():
    assert playhdl.__version__ == utils.get_pkg_version()


class TestJson:
    @pytest.fixture
    def test_file(self, tmp_path: Path) -> Path:
        return tmp_path.joinpath("data.json")

    class TestEnum(Enum):
        __test__ = False
        A = 0
        B = 1

    class TestCustomClass:
        pass

    def test_invalid_encoding(self, test_file: Path):
        data = {
            "custom_class": self.TestCustomClass(),
        }
        json_file = test_file
        with pytest.raises(TypeError):
            utils.dump_json(json_file, data)

    def test_valid_encoding(self, test_file: Path):
        data = {
            "foo_path": Path("/tmp"),
            "bar_enum": self.TestEnum.A,
            "baz_dict": {"answer": 42},
        }
        json_file = test_file
        utils.dump_json(json_file, data)
        loaded_data = utils.load_json(json_file)
        loaded_data["foo_path"] = Path(loaded_data["foo_path"])
        loaded_data["bar_enum"] = self.TestEnum[loaded_data["bar_enum"]]
        assert data == loaded_data


class TestIsWriteAllowed:
    @pytest.fixture
    def test_file(self, tmp_path: Path) -> Path:
        return tmp_path.joinpath("query_test_file")

    def test_query_true(self, test_file: Path, monkeypatch: pytest.MonkeyPatch):
        test_file.touch()
        monkeypatch.setattr("sys.stdin", StringIO("a\nb\ny"))
        assert utils.is_write_allowed(test_file) is True

    def test_query_false(self, test_file: Path, monkeypatch: pytest.MonkeyPatch):
        test_file.touch()
        monkeypatch.setattr("sys.stdin", StringIO("a\nc\nn"))
        assert utils.is_write_allowed(test_file) is False

    def test_query_force_true(self, test_file: Path, monkeypatch: pytest.MonkeyPatch):
        test_file.touch()
        monkeypatch.setattr("sys.stdin", StringIO("a\nc\nn"))
        assert utils.is_write_allowed(test_file, force_yes=True) is True

    def test_query_not_exist(self, test_file: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("sys.stdin", StringIO("a\nc\nn"))
        assert utils.is_write_allowed(test_file) is True


class TestExtendedEnum:
    class Foo(utils.ExtendedEnum):
        ABC = enum.auto()
        XYZ = enum.auto()

    def test_values(self):
        assert self.Foo.ABC.value == "abc"
        assert self.Foo.XYZ.value == "xyz"

    def test_as_str(self):
        assert str(self.Foo.ABC) == "abc"
        assert str(self.Foo.XYZ) == "xyz"

    def test_as_list(self):
        assert self.Foo.aslist() == ["abc", "xyz"]
