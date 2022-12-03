from __future__ import annotations
from typing import List, Dict, Optional, Type
from pathlib import Path
from dataclasses import dataclass
import enum
import shutil
from abc import ABC, abstractmethod, abstractclassmethod


from . import utils
from . import templates


class ToolKind(utils.ExtendedEnum):
    modelsim = enum.auto()
    xcelium = enum.auto()
    verilator = enum.auto()
    icarus = enum.auto()
    vcs = enum.auto()
    vivado = enum.auto()


@dataclass
class ToolDescriptor:
    kind: ToolKind
    bin_dir: Path


ToolPool = Dict[str, ToolDescriptor]


def find_tool_dir(tool_kind: ToolKind) -> Optional[Path]:
    """Try to find a directory with executables for the provided tool"""
    return _Tool.get_subclass_by_kind(tool_kind)().find_bin_dir()


def generate_script(tool_kind: ToolKind, design_kind: templates.DesignKind, sources: List[str]) -> List[str]:
    """Generate script for the provided tool and design"""
    return _Tool.get_subclass_by_kind(tool_kind)().generate_script(design_kind, sources)


def generate_all_possible_scripts(design_kind: templates.DesignKind, sources: List[str]) -> Dict[str, List[str]]:
    """Generate all posible tool scripts for the provided design"""
    scripts = {}
    for tool in ToolKind:
        try:
            scripts[tool] = generate_script(tool, design_kind, sources)
        except ValueError:
            pass
    return scripts


class _Tool(ABC):
    """Generic tool"""

    @abstractmethod
    def generate_script(self, design_kind: templates.DesignKind, sources: List[str], **kwargs) -> List[str]:
        """Generate list of commands to perform tool execution"""
        raise NotImplementedError

    @abstractclassmethod
    def get_kind(cls) -> ToolKind:
        """Get kind of the tool"""
        raise NotImplementedError

    @abstractclassmethod
    def get_base_exe_name(cls) -> str:
        """Get name of the basic executable"""
        raise NotImplementedError

    @classmethod
    def get_subclass_by_kind(cls, tool_kind: ToolKind) -> Type[_Tool]:
        """Get template class according to design kind"""
        for cls in _Tool.__subclasses__():
            if cls.get_kind() == tool_kind:
                return cls
        raise ValueError(f"Can't find tool class for tool_kind={tool_kind}")

    def find_bin_dir(self) -> Optional[Path]:
        """Try to find a directory with executables for the provided tool"""
        bin_dir = shutil.which(self.get_base_exe_name())
        return Path(bin_dir) if bin_dir else None


class _Icarus(_Tool):
    """Icarus Verilog"""

    def generate_script(self, design_kind: templates.DesignKind, sources: List[str], **kwargs) -> List[str]:
        if design_kind not in (templates.DesignKind.verilog, templates.DesignKind.systemverilog):
            raise ValueError(f"Icarus doesn't support provided design kind '{design_kind}'")

        if design_kind == templates.DesignKind.verilog:
            lang_ver = "-g2001"
        elif design_kind == templates.DesignKind.systemverilog:
            lang_ver = "-g2012"

        build_cmd = f"iverilog -Wall {lang_ver} {' '.join(sources)} -o tb.out"
        sim_cmd = "vvp tb.out"

        return [build_cmd, sim_cmd]

    @classmethod
    def get_kind(cls) -> ToolKind:
        return ToolKind.icarus

    @classmethod
    def get_base_exe_name(cls) -> str:
        return "iverilog"


class _Modelsim(_Tool):
    """Siemens (Mentor Grapthics) Modelsim"""

    def generate_script(self, design_kind: templates.DesignKind, sources: List[str], **kwargs) -> List[str]:
        raise NotImplementedError

    @classmethod
    def get_kind(cls) -> ToolKind:
        return ToolKind.modelsim

    @classmethod
    def get_base_exe_name(cls) -> str:
        return "vsim"


class _Xcelium(_Tool):
    """Cadence Xcelium"""

    def generate_script(self, design_kind: templates.DesignKind, sources: List[str], **kwargs) -> List[str]:
        raise NotImplementedError

    @classmethod
    def get_kind(cls) -> ToolKind:
        return ToolKind.xcelium

    @classmethod
    def get_base_exe_name(cls) -> str:
        return "xmsim"


class _Verilator(_Tool):
    """Veripool Verilator"""

    def generate_script(self, design_kind: templates.DesignKind, sources: List[str], **kwargs) -> List[str]:
        raise NotImplementedError

    @classmethod
    def get_kind(cls) -> ToolKind:
        return ToolKind.verilator

    @classmethod
    def get_base_exe_name(cls) -> str:
        return "verilator"


class _Vcs(_Tool):
    """Synopsys VCS"""

    def generate_script(self, design_kind: templates.DesignKind, sources: List[str], **kwargs) -> List[str]:
        raise NotImplementedError

    @classmethod
    def get_kind(cls) -> ToolKind:
        return ToolKind.vcs

    @classmethod
    def get_base_exe_name(cls) -> str:
        return "vcs"


class _Vivado(_Tool):
    """Xilinx Vivado"""

    def generate_script(self, design_kind: templates.DesignKind, sources: List[str], **kwargs) -> List[str]:
        raise NotImplementedError

    @classmethod
    def get_kind(cls) -> ToolKind:
        return ToolKind.vivado

    @classmethod
    def get_base_exe_name(cls) -> str:
        return "xsim"
