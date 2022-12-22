from __future__ import annotations

import dataclasses
import enum
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from . import templates, utils


@dataclass
class ToolSettings:
    kind: ToolKind
    bin_dir: Path
    env: Dict[str, str] = dataclasses.field(default_factory=dict)
    extras: Dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        self.bin_dir = Path(self.bin_dir)
        self.kind = ToolKind(self.kind)


class ToolKind(utils.ExtendedEnum):
    MODELSIM = enum.auto()
    XCELIUM = enum.auto()
    VERILATOR = enum.auto()
    ICARUS = enum.auto()
    VCS = enum.auto()
    VIVADO = enum.auto()


@dataclass
class ToolScript:
    build: List[str]
    sim: List[str]
    waves: List[str]


ToolUid = str


def find_tool_dir(tool_kind: ToolKind) -> Optional[Path]:
    """Try to find a directory with executables for the provided tool"""
    return _Tool.get_subclass_by_kind(tool_kind).find_bin_dir()


def generate_script(settings: ToolSettings, design_kind: templates.DesignKind, sources: List[str]) -> ToolScript:
    """Generate script for the provided tool and design"""
    return _Tool.get_subclass_by_kind(settings.kind)(settings).generate_script(design_kind, sources)


def get_compatibility_text_table() -> str:
    """Create text table with tool kinds vs design kind compatibility"""
    col_full_w = 15
    col_text_w = col_full_w - 2

    design_kinds_str = [f"{k.value:^{col_text_w}}" for k in templates.DesignKind]
    header = f"| {'':>{col_text_w}} | {' | '.join(design_kinds_str)}" + " |"

    col_dashes = "-" * col_text_w
    divider = f"| {col_dashes} | {' | '.join([col_dashes] * len(design_kinds_str))}" + " |"

    rows = []
    for tool in ToolKind:
        tool_cls = _Tool.get_subclass_by_kind(tool)
        tool_col = f"{tool.value:>{col_text_w}}"
        compat_cols = []
        for design in templates.DesignKind:
            is_compatible = "X" if design in tool_cls.get_supported_design_kinds() else ""
            compat_cols.append(f"{is_compatible:^{col_text_w}}")
        rows.append(f"| {tool_col} | {' | '.join(compat_cols)}" + " |")

    return "\n".join([header, divider] + rows)


class _Tool(ABC):
    """Generic tool"""

    @abstractmethod
    def __init__(self, settings: ToolSettings) -> None:
        self.settings = settings
        if self.settings.kind != self.get_kind():
            raise RuntimeError(
                f"Provided tool kind '{self.settings.kind}' within settings "
                f"doesn't match with expected value of '{self.get_kind()}'"
            )

    @abstractmethod
    def generate_script(self, design_kind: templates.DesignKind, sources: List[str], **kwargs: Any) -> ToolScript:
        """Generate list of commands to perform tool execution"""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_kind(cls) -> ToolKind:
        """Get kind of the tool"""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_base_exe_name(cls) -> str:
        """Get name of the basic executable"""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_supported_design_kinds(cls) -> List[templates.DesignKind]:
        """Get supported design kinds for the tool"""
        raise NotImplementedError

    @classmethod
    def get_subclass_by_kind(cls, tool_kind: ToolKind) -> Type[_Tool]:
        """Get template class according to tool kind"""
        for cls in _Tool.__subclasses__():  # type: ignore
            if cls.get_kind() == tool_kind:
                return cls
        raise ValueError(f"Can't find tool class for tool_kind={tool_kind}")

    @classmethod
    def find_bin_dir(cls) -> Optional[Path]:
        """Try to find a directory with executables for the provided tool"""
        bin_dir = shutil.which(cls.get_base_exe_name())
        return Path(bin_dir).parent if bin_dir else None

    @classmethod
    def _validate_design_kind(cls, design_kind: templates.DesignKind) -> None:
        """Check that this design kind is supported by the tool"""
        if design_kind not in cls.get_supported_design_kinds():
            raise ValueError(f"{cls.get_kind()} doesn't support provided design kind '{design_kind}'")

    @classmethod
    def _patch_sources(cls, sources: List[str]) -> List[str]:
        """Patch paths to sources"""
        return [f"../{s}" for s in sources]

    @classmethod
    def _stringify_sources(cls, sources: List[str], separator: str = " ") -> str:
        """Convert list of sources to a string"""
        return separator.join(sources)


class _Icarus(_Tool):
    """Icarus Verilog"""

    def __init__(self, settings: ToolSettings) -> None:
        super().__init__(settings)

    def generate_script(self, design_kind: templates.DesignKind, sources: List[str], **kwargs: Any) -> ToolScript:
        self._validate_design_kind(design_kind)

        lang_ver = "-g2001"  # verilog by default
        if design_kind == templates.DesignKind.sv:
            lang_ver = "-g2012"

        sources_opts = self._stringify_sources(self._patch_sources(sources))
        build_cmds = [f"iverilog -Wall {lang_ver} {sources_opts} -o tb.out"]
        sim_cmds = ["vvp tb.out"]
        waves_cmds = ["gtkwave tb.vcd"]

        return ToolScript(build=build_cmds, sim=sim_cmds, waves=waves_cmds)

    @classmethod
    def get_supported_design_kinds(cls) -> List[templates.DesignKind]:
        return [templates.DesignKind.verilog, templates.DesignKind.sv]

    @classmethod
    def get_kind(cls) -> ToolKind:
        return ToolKind.ICARUS

    @classmethod
    def get_base_exe_name(cls) -> str:
        return "iverilog"


class _Modelsim(_Tool):
    """Siemens (Mentor Grapthics) Modelsim"""

    def __init__(self, settings: ToolSettings) -> None:
        super().__init__(settings)

    def generate_script(self, design_kind: templates.DesignKind, sources: List[str], **kwargs: Any) -> ToolScript:
        self._validate_design_kind(design_kind)

        vlog_opts = ""
        if design_kind == templates.DesignKind.sv:
            vlog_opts = "-sv"

        build_cmds = ["vlib worklib", "vmap work worklib"]
        for s in self._patch_sources(sources):
            if design_kind in (templates.DesignKind.verilog, templates.DesignKind.sv):
                build_cmds.append(f"vlog {vlog_opts} {s}")

        sim_cmds = ['vsim -c worklib.tb -do "log -r *;run -all"']
        waves_cmds = ["vsim -view vsim.wlf"]

        return ToolScript(build=build_cmds, sim=sim_cmds, waves=waves_cmds)

    @classmethod
    def get_supported_design_kinds(cls) -> List[templates.DesignKind]:
        return [templates.DesignKind.verilog, templates.DesignKind.sv]

    @classmethod
    def get_kind(cls) -> ToolKind:
        return ToolKind.MODELSIM

    @classmethod
    def get_base_exe_name(cls) -> str:
        return "vsim"


class _Xcelium(_Tool):
    """Cadence Xcelium"""

    def __init__(self, settings: ToolSettings) -> None:
        super().__init__(settings)

    def generate_script(self, design_kind: templates.DesignKind, sources: List[str], **kwargs: Any) -> ToolScript:
        self._validate_design_kind(design_kind)

        vlog_opts = ""
        if design_kind == templates.DesignKind.sv:
            vlog_opts = "-sv"

        build_cmds = []
        for s in self._patch_sources(sources):
            if design_kind in (templates.DesignKind.verilog, templates.DesignKind.sv):
                build_cmds.append(f"xmvlog {vlog_opts} {s}")
        build_cmds.append("xmelab -access +rwc -snapshot tbsim tb")

        sim_cmds = ["xmsim tbsim"]

        waves_cmds = [
            'echo "database open -overwrite tb.vcd" > waves.cmd',
            "simvision -input waves.cmd -waves",
        ]

        return ToolScript(build=build_cmds, sim=sim_cmds, waves=waves_cmds)

    @classmethod
    def get_supported_design_kinds(cls) -> List[templates.DesignKind]:
        return [templates.DesignKind.verilog, templates.DesignKind.sv]

    @classmethod
    def get_kind(cls) -> ToolKind:
        return ToolKind.XCELIUM

    @classmethod
    def get_base_exe_name(cls) -> str:
        return "xmsim"


class _Verilator(_Tool):
    """Veripool Verilator"""

    def __init__(self, settings: ToolSettings) -> None:
        super().__init__(settings)

    def generate_script(self, design_kind: templates.DesignKind, sources: List[str], **kwargs: Any) -> ToolScript:
        self._validate_design_kind(design_kind)

        lang_ver = "+verilog2001ext+v"  # verilog by default
        if design_kind == templates.DesignKind.sv:
            lang_ver = "+systemverilogext+sv"

        sources_opts = self._stringify_sources(self._patch_sources(sources))
        build_cmds = [f"verilator {lang_ver} --trace --binary -j 0 {sources_opts}"]
        sim_cmds = ["./obj_dir/Vtb"]
        waves_cmds = ["gtkwave tb.vcd"]

        return ToolScript(build=build_cmds, sim=sim_cmds, waves=waves_cmds)

    @classmethod
    def get_supported_design_kinds(cls) -> List[templates.DesignKind]:
        return [templates.DesignKind.verilog, templates.DesignKind.sv]

    @classmethod
    def get_kind(cls) -> ToolKind:
        return ToolKind.VERILATOR

    @classmethod
    def get_base_exe_name(cls) -> str:
        return "verilator"


class _Vcs(_Tool):
    """Synopsys VCS"""

    class _GuiKind(utils.ExtendedEnum):
        DVE = enum.auto()
        VERDI = enum.auto()

    def __init__(self, settings: ToolSettings) -> None:
        super().__init__(settings)
        self.gui = self._GuiKind(settings.extras.get("gui", "verdi"))

    def generate_script(self, design_kind: templates.DesignKind, sources: List[str], **kwargs: Any) -> ToolScript:
        self._validate_design_kind(design_kind)

        vlog_opts = ""
        if design_kind == templates.DesignKind.sv:
            vlog_opts = "-sverilog"
        elif design_kind == templates.DesignKind.sv_uvm12:
            vlog_opts = "-sverilog -ntb_opts uvm-1.2"

        sources_opts = self._stringify_sources(self._patch_sources(sources))
        build_cmds = [f"vcs -full64 {vlog_opts} -debug_acc+all +vcs+vcdpluson +vcs+fsdbon {sources_opts}"]

        sim_cmds = ["./simv"]

        if self.gui == self._GuiKind.VERDI:
            waves_cmds = ["verdi -ssf novas.fsdb"]
        else:
            waves_cmds = ["dve -vpd vcdplus.vpd"]

        return ToolScript(build=build_cmds, sim=sim_cmds, waves=waves_cmds)

    @classmethod
    def get_supported_design_kinds(cls) -> List[templates.DesignKind]:
        return [
            templates.DesignKind.verilog,
            templates.DesignKind.sv,
            templates.DesignKind.sv_uvm12,
        ]

    @classmethod
    def get_kind(cls) -> ToolKind:
        return ToolKind.VCS

    @classmethod
    def get_base_exe_name(cls) -> str:
        return "vcs"


class _Vivado(_Tool):
    """Xilinx Vivado"""

    def __init__(self, settings: ToolSettings) -> None:
        super().__init__(settings)

    def generate_script(self, design_kind: templates.DesignKind, sources: List[str], **kwargs: Any) -> ToolScript:
        self._validate_design_kind(design_kind)

        uvm_vlog_opts = ""
        uvm_elab_opts = ""
        if design_kind == templates.DesignKind.sv_uvm12:
            uvm_vlog_opts = "-uvm_version 1.2 -L uvm"
            uvm_elab_opts = "-L uvm"

        build_cmds = []
        for s in self._patch_sources(sources):
            if design_kind == templates.DesignKind.verilog:
                build_cmds.append(f"xvlog -work worklib {s}")
            elif design_kind in [templates.DesignKind.sv, templates.DesignKind.sv_uvm12]:
                build_cmds.append(f"xvlog -work worklib -sv {uvm_vlog_opts} {s}")
        build_cmds.append(f"xelab worklib.tb {uvm_elab_opts} --debug all -s tbsim")

        sim_cmds = [
            'echo "log_wave -recursive *;run all;quit" > sim.tcl',
            "xsim tbsim --wdb tb.wdb --t sim.tcl",
        ]

        waves_cmds = [
            'echo "open_wave_database tb.wdb" > waves.tcl',
            "vivado -source waves.tcl",
        ]

        return ToolScript(build=build_cmds, sim=sim_cmds, waves=waves_cmds)

    @classmethod
    def get_supported_design_kinds(cls) -> List[templates.DesignKind]:
        return [
            templates.DesignKind.verilog,
            templates.DesignKind.sv,
            templates.DesignKind.sv_uvm12,
        ]

    @classmethod
    def get_kind(cls) -> ToolKind:
        return ToolKind.VIVADO

    @classmethod
    def get_base_exe_name(cls) -> str:
        return "xsim"
