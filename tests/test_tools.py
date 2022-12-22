"""Tests for playhdl/tools.py
"""

import shutil
from pathlib import Path

import playhdl.templates as templates

import playhdl.tools as tools

import pytest


def _get_base_exe_name(tool_kind: tools.ToolKind) -> str:
    return {
        tools.ToolKind.ICARUS: "iverilog",
        tools.ToolKind.MODELSIM: "vsim",
        tools.ToolKind.VCS: "vcs",
        tools.ToolKind.XCELIUM: "xmsim",
        tools.ToolKind.VIVADO: "xsim",
        tools.ToolKind.VERILATOR: "verilator",
    }[tool_kind]


@pytest.mark.parametrize("tool_kind", tools.ToolKind.aslist())
def test_find_tool_dir(tool_kind: tools.ToolKind):
    bin_path = shutil.which(_get_base_exe_name(tool_kind))
    expected = Path(bin_path).parent if bin_path else None
    assert tools.find_tool_dir(tool_kind) == expected


def test_get_compatibility_text_table():
    table = tools.get_compatibility_text_table()
    for k in tools.ToolKind:
        assert str(k) in table
    for k in templates.DesignKind:
        assert str(k) in table


class TestTool:
    def test_abc(self):
        with pytest.raises(NotImplementedError):
            tools._Tool.get_kind()
        with pytest.raises(NotImplementedError):
            tools._Tool.get_base_exe_name()
        with pytest.raises(NotImplementedError):
            tools._Tool.get_supported_design_kinds()
        with pytest.raises(NotImplementedError):
            tools._Tool.generate_script(None, None, None)  # type: ignore

    @pytest.mark.parametrize("kind", tools.ToolKind.aslist())
    def test_settings_wrong_kind(self, kind: tools.ToolKind):
        # get wrong kind
        members = list(tools.ToolKind)
        wrong_index = members.index(kind) + 1
        if wrong_index >= len(members):
            wrong_index = 0
        wrong_kind = members[wrong_index]

        settings = tools.ToolSettings(kind=wrong_kind, bin_dir=Path("/usr/bin"), env={}, extras={})

        with pytest.raises(RuntimeError):
            tools._Tool.get_subclass_by_kind(kind)(settings)

    def test_subclass_wrong_kind(self):
        with pytest.raises(ValueError):
            tools._Tool.get_subclass_by_kind("foo")  # type: ignore


class _TestGenerateScript:
    @pytest.fixture
    def settings(self) -> tools.ToolSettings:
        raise NotImplementedError

    def _assert_script(self, script: tools.ToolScript) -> None:
        assert len(script.build) > 0
        for step in script.build:
            assert step != ""
        assert len(script.sim) > 0
        for step in script.sim:
            assert step != ""
        assert len(script.waves) > 0
        for step in script.waves:
            assert step != ""

    def test_verilog(self, settings: tools.ToolSettings):
        script = tools.generate_script(settings, templates.DesignKind.verilog, ["tb.v"])
        self._assert_script(script)

    def test_sv(self, settings: tools.ToolSettings):
        script = tools.generate_script(settings, templates.DesignKind.sv, ["tb.sv"])
        self._assert_script(script)

    def test_sv_uvm12(self, settings: tools.ToolSettings):
        script = tools.generate_script(settings, templates.DesignKind.sv_uvm12, ["tb_uvm12.sv"])
        self._assert_script(script)

    def test_vhdl(self, settings: tools.ToolSettings):
        script = tools.generate_script(settings, templates.DesignKind.vhdl, ["tb.vhd"])
        self._assert_script(script)


class TestGenerateScriptIcarus(_TestGenerateScript):
    @pytest.fixture
    def settings(self) -> tools.ToolSettings:
        return tools.ToolSettings(kind=tools.ToolKind.ICARUS, bin_dir=Path("/usr/bin"), env={}, extras={})

    def test_sv_uvm12(self, settings: tools.ToolSettings):
        with pytest.raises(ValueError):
            super().test_sv_uvm12(settings)

    def test_vhdl(self, settings: tools.ToolSettings):
        with pytest.raises(ValueError):
            super().test_vhdl(settings)


class TestGenerateScriptVerilator(_TestGenerateScript):
    @pytest.fixture
    def settings(self) -> tools.ToolSettings:
        return tools.ToolSettings(kind=tools.ToolKind.VERILATOR, bin_dir=Path("/usr/bin"), env={}, extras={})

    def test_sv_uvm12(self, settings: tools.ToolSettings):
        with pytest.raises(ValueError):
            super().test_sv_uvm12(settings)

    def test_vhdl(self, settings: tools.ToolSettings):
        with pytest.raises(ValueError):
            super().test_vhdl(settings)


class TestGenerateScriptModelsim(_TestGenerateScript):
    @pytest.fixture
    def settings(self) -> tools.ToolSettings:
        return tools.ToolSettings(kind=tools.ToolKind.MODELSIM, bin_dir=Path("/usr/bin"), env={}, extras={})

    def test_sv_uvm12(self, settings: tools.ToolSettings):
        with pytest.raises(ValueError):
            super().test_sv_uvm12(settings)

    def test_vhdl(self, settings: tools.ToolSettings):
        with pytest.raises(ValueError):
            super().test_vhdl(settings)


class TestGenerateScriptXcelium(_TestGenerateScript):
    @pytest.fixture
    def settings(self) -> tools.ToolSettings:
        return tools.ToolSettings(kind=tools.ToolKind.XCELIUM, bin_dir=Path("/usr/bin"), env={}, extras={})

    def test_sv_uvm12(self, settings: tools.ToolSettings):
        with pytest.raises(ValueError):
            super().test_sv_uvm12(settings)

    def test_vhdl(self, settings: tools.ToolSettings):
        with pytest.raises(ValueError):
            super().test_vhdl(settings)


class TestGenerateScriptVcs(_TestGenerateScript):
    @pytest.fixture
    def settings(self) -> tools.ToolSettings:
        return tools.ToolSettings(kind=tools.ToolKind.VCS, bin_dir=Path("/usr/bin"), env={}, extras={})

    def test_vhdl(self, settings: tools.ToolSettings):
        with pytest.raises(ValueError):
            super().test_vhdl(settings)

    @pytest.mark.parametrize("gui", ["verdi", "dve"])
    def test_extras_gui(self, settings: tools.ToolSettings, gui: str):
        settings.extras["gui"] = gui
        script = tools.generate_script(settings, templates.DesignKind.verilog, ["tb.v"])
        for step in script.waves:
            if gui in step:
                break
        else:
            raise ValueError(f"{gui} executable should be inside waves part of the script")


class TestGenerateScriptVivado(_TestGenerateScript):
    @pytest.fixture
    def settings(self) -> tools.ToolSettings:
        return tools.ToolSettings(kind=tools.ToolKind.VIVADO, bin_dir=Path("/usr/bin"), env={}, extras={})

    def test_vhdl(self, settings: tools.ToolSettings):
        with pytest.raises(ValueError):
            super().test_vhdl(settings)
