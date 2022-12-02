from typing import List, Tuple, Dict
from pathlib import Path
import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
import sys
import inspect

from .. import log
from .. import utils


class DesignKind(utils.ExtendedEnum):
    verilog = enum.auto()
    systemverilog = enum.auto()
    vhdl = enum.auto()


class LibraryKind(utils.ExtendedEnum):
    nolib = enum.auto()
    uvm12 = enum.auto()


@dataclass
class TemplateDescriptor:
    filename: str
    content: str


class DesignTemplate(ABC):
    """Generic template"""

    @abstractmethod
    def generate(self, lib: LibraryKind, **kwargs) -> List[TemplateDescriptor]:
        """Generate design template files"""
        pass

    @abstractmethod
    def get_kind(self) -> DesignKind:
        """Get kind of the template"""
        pass

    def _read_template_file(self, filename: str) -> str:
        """Read provided template file"""
        with Path(__file__).parent.joinpath(filename).open("r") as f:
            return f.read()


class Verilog(DesignTemplate):
    """Verilog design template"""

    def generate(self, lib: LibraryKind, **kwargs) -> List[TemplateDescriptor]:
        """Generate design template files"""
        # No external libraries are supported
        if lib != LibraryKind.nolib:
            raise ValueError("No external libraries are supported")

        content = self._read_template_file("tb.v")
        return [TemplateDescriptor("tb.v", content)]

    def get_kind(self) -> DesignKind:
        """Get kind of the template"""
        return DesignKind.verilog


class SystemVerilog(DesignTemplate):
    """SystemVerilog design template"""

    def generate(self, lib: LibraryKind, **kwargs) -> List[TemplateDescriptor]:
        """Generate design template files"""
        # No external libraries are supported
        if lib != LibraryKind.nolib:
            raise ValueError("No external libraries are supported")

        content = self._read_template_file("tb.sv")
        return [TemplateDescriptor("tb.sv", content)]

    def get_kind(self) -> DesignKind:
        """Get kind of the template"""
        return DesignKind.systemverilog


def get_templates(design_kind: DesignKind, lib: LibraryKind) -> List[TemplateDescriptor]:
    """Get template files according to design kind"""
    for cls in utils.get_module_sublcasses(__name__, DesignTemplate):
        obj = cls()
        if obj.get_kind() == design_kind:
            return obj.generate(lib)
    raise ValueError(f"Can't find template for design_kind={design_kind}")
