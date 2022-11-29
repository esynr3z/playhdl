import typing
from typing import Literal, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import shutil


from . import log

ToolKind = Literal[
    "modelsim",
    "xcelium",
    "verilator",
    "icarus",
    "vcs",
    "vivado",
]

DesignMode = Literal[
    "verilog",
    "systemverilog",
    "vhdl",
]

LibraryKind = Literal[
    "none",
    "uvm12",
]


@dataclass
class ToolDescriptor:
    kind: ToolKind
    bin_dir: Path


ToolPool = Dict[str, ToolDescriptor]


def get_all_tool_kinds() -> Tuple[ToolKind]:
    return typing.get_args(ToolKind)


def find_tool_dir(tool: ToolKind) -> Optional[Path]:
    """Try to find a directory with executables for the provided tool"""
    try:
        exec = {
            "modelsim": "vsim",
            "xcelium": "xmsim",
            "verilator": "verilator",
            "icarus": "iverilog",
            "vcs": "vcs",
            "vivado": "xsim",
        }[tool]
    except KeyError:
        raise KeyError(f"Unknown tool '{tool}'. Don't know what executable is.")

    bin_dir = shutil.which(exec)
    return Path(bin_dir) if bin_dir else None
