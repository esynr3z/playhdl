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


class TestTool:
    def test_abc(self):
        with pytest.raises(NotImplementedError):
            _Tool.get_kind()
        with pytest.raises(NotImplementedError):
            _Tool.get_base_exe_name()
        with pytest.raises(NotImplementedError):
            _Tool.get_supported_design_kinds()
        with pytest.raises(NotImplementedError):
            _Tool.generate_script(None, None, None)  # type: ignore

    @pytest.mark.parametrize("kind", ToolKind.aslist())
    def test_settings_wrong_kind(self, kind: ToolKind):
        # get wrong kind
        members = list(ToolKind)
        wrong_index = members.index(kind) + 1
        if wrong_index >= len(members):
            wrong_index = 0
        wrong_kind = members[wrong_index]

        settings = ToolSettings(kind=wrong_kind, bin_dir=Path("/usr/bin"), env={}, extras={})

        with pytest.raises(RuntimeError):
            _Tool.get_subclass_by_kind(kind)(settings)

    def test_subclass_wrong_kind(self):
        with pytest.raises(ValueError):
            _Tool.get_subclass_by_kind("foo")  # type: ignore


class _TestGenerateScript:
    @pytest.fixture
    def settings(self) -> ToolSettings:
        raise NotImplementedError

    def _assert_script(self, script: ToolScript):
        assert len(script.build) > 0
        for step in script.build:
            assert step != ""
        assert len(script.sim) > 0
        for step in script.sim:
            assert step != ""
        assert len(script.waves) > 0
        for step in script.waves:
            assert step != ""

    def test_verilog(self, settings: ToolSettings) -> ToolScript:
        script = generate_script(settings, templates.DesignKind.verilog, ["tb.v"])
        self._assert_script(script)
        return script

    def test_sv(self, settings: ToolSettings) -> ToolScript:
        script = generate_script(settings, templates.DesignKind.sv, ["tb.sv"])
        self._assert_script(script)
        return script

    def test_sv_uvm12(self, settings: ToolSettings) -> ToolScript:
        script = generate_script(settings, templates.DesignKind.sv_uvm12, ["tb_uvm12.sv"])
        self._assert_script(script)
        return script

    def test_vhdl(self, settings: ToolSettings) -> ToolScript:
        script = generate_script(settings, templates.DesignKind.vhdl, ["tb.vhd"])
        self._assert_script(script)
        return script


class TestGenerateScriptIcarus(_TestGenerateScript):
    @pytest.fixture
    def settings(self) -> ToolSettings:
        return ToolSettings(kind=ToolKind.ICARUS, bin_dir=Path("/usr/bin"), env={}, extras={})

    def test_sv_uvm12(self, settings: ToolSettings):
        with pytest.raises(ValueError):
            super().test_sv_uvm12(settings)

    def test_vhdl(self, settings: ToolSettings):
        with pytest.raises(ValueError):
            super().test_vhdl(settings)


class TestGenerateScriptVerilator(_TestGenerateScript):
    @pytest.fixture
    def settings(self) -> ToolSettings:
        return ToolSettings(kind=ToolKind.VERILATOR, bin_dir=Path("/usr/bin"), env={}, extras={})

    def test_sv_uvm12(self, settings: ToolSettings):
        with pytest.raises(ValueError):
            super().test_sv_uvm12(settings)

    def test_vhdl(self, settings: ToolSettings):
        with pytest.raises(ValueError):
            super().test_vhdl(settings)


class TestGenerateScriptModelsim(_TestGenerateScript):
    @pytest.fixture
    def settings(self) -> ToolSettings:
        return ToolSettings(kind=ToolKind.MODELSIM, bin_dir=Path("/usr/bin"), env={}, extras={})

    def test_sv_uvm12(self, settings: ToolSettings):
        with pytest.raises(ValueError):
            super().test_sv_uvm12(settings)

    def test_vhdl(self, settings: ToolSettings):
        with pytest.raises(ValueError):
            super().test_vhdl(settings)


class TestGenerateScriptXcelium(_TestGenerateScript):
    @pytest.fixture
    def settings(self) -> ToolSettings:
        return ToolSettings(kind=ToolKind.XCELIUM, bin_dir=Path("/usr/bin"), env={}, extras={})

    def test_sv_uvm12(self, settings: ToolSettings):
        with pytest.raises(ValueError):
            super().test_sv_uvm12(settings)

    def test_vhdl(self, settings: ToolSettings):
        with pytest.raises(ValueError):
            super().test_vhdl(settings)


class TestGenerateScriptVcs(_TestGenerateScript):
    @pytest.fixture
    def settings(self) -> ToolSettings:
        return ToolSettings(kind=ToolKind.VCS, bin_dir=Path("/usr/bin"), env={}, extras={})

    def test_vhdl(self, settings: ToolSettings):
        with pytest.raises(ValueError):
            super().test_vhdl(settings)

    @pytest.mark.parametrize("gui", ["verdi", "dve"])
    def test_extras_gui(self, settings: ToolSettings, gui: str):
        settings.extras["gui"] = gui
        script = super().test_verilog(settings)
        for step in script.waves:
            if gui in step:
                break
        else:
            raise ValueError(f"{gui} executable should be inside waves part of the script")


class TestGenerateScriptVivado(_TestGenerateScript):
    @pytest.fixture
    def settings(self) -> ToolSettings:
        return ToolSettings(kind=ToolKind.VIVADO, bin_dir=Path("/usr/bin"), env={}, extras={})

    def test_vhdl(self, settings: ToolSettings):
        with pytest.raises(ValueError):
            super().test_vhdl(settings)
