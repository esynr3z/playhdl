import typing
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import enum
from enum import Enum
import shutil


from . import log
from . import utils


class ToolKind(utils.ExtendedEnum):
    modelsim = enum.auto()
    xcelium = enum.auto()
    verilator = enum.auto()
    icarus = enum.auto()
    vcs = enum.auto()
    vivado = enum.auto()


class DesignMode(utils.ExtendedEnum):
    verilog = enum.auto()
    systemverilog = enum.auto()
    vhdl = enum.auto()


class LibraryKind(utils.ExtendedEnum):
    nolib = enum.auto()
    uvm12 = enum.auto()


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
