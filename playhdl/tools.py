import typing
from typing import List, Dict, Optional, Type
from pathlib import Path
from dataclasses import dataclass
import enum
from enum import Enum
import shutil
from abc import ABC, abstractmethod


from . import log
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


def find_tool_dir(tool: ToolKind) -> Optional[Path]:
    """Try to find a directory with executables for the provided tool"""
    try:
        exec = {
            ToolKind.modelsim: "vsim",
            ToolKind.xcelium: "xmsim",
            ToolKind.verilator: "verilator",
            ToolKind.icarus: "iverilog",
            ToolKind.vcs: "vcs",
            ToolKind.vivado: "xsim",
        }[tool]
    except KeyError:
        raise KeyError(f"Unknown tool '{tool}'. Don't know what executable is.")

    bin_dir = shutil.which(exec)
    return Path(bin_dir) if bin_dir else None


class Tool(ABC):
    """Generic tool"""

    @abstractmethod
    def generate_script(self, design_kind: templates.DesignKind, lib: templates.LibraryKind, **kwargs) -> List[str]:
        """Generate list of commands to perform tool execution"""
        pass

    @abstractmethod
    def get_kind(self) -> ToolKind:
        """Get kind of the tool"""
        pass

    @abstractmethod
    def get_basic_exe_name(self) -> str:
        """Get name of the basic executable"""
        pass


def get_tool(kind: ToolKind) -> type(Tool):
    """Get template files according to design kind"""
    pass


class Icarus(Tool):
    """Icarus Verilog"""

    def generate_script(self, design_kind: templates.DesignKind, lib: templates.LibraryKind, **kwargs) -> List[str]:
        """Generate list of commands to perform tool execution"""
        # No external libraries are supported
        if lib != templates.LibraryKind.nolib:
            raise ValueError

        script = []
        if design_kind == templates.DesignKind.verilog:
            script.append("iverilog -Wall -g2001 tb.v -o tb.out")
        elif design_kind == templates.DesignKind.systemverilog:
            script.append("iverilog -Wall -g2012 tb.sv -o tb.out")
        else:
            raise ValueError
        script.append("vvp tb.out")

        return script

    def get_kind(self) -> ToolKind:
        """Get kind of the tool"""
        return ToolKind.icarus
