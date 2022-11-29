from __future__ import annotations
from typing import Literal, Dict
from pathlib import Path
from dataclasses import dataclass


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
