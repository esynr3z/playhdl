from __future__ import annotations
from typing import List, Type
from pathlib import Path
import enum
from abc import ABC, abstractmethod, abstractclassmethod
from dataclasses import dataclass

from .. import utils


class DesignKind(utils.ExtendedEnum):
    verilog = enum.auto()
    systemverilog = enum.auto()
    systemverilog_uvm12 = enum.auto()
    vhdl = enum.auto()


@dataclass
class TemplateDescriptor:
    filename: str
    content: str


def generate_templates(design_kind: DesignKind) -> List[TemplateDescriptor]:
    """Get template files according to design kind"""
    return _DesignTemplate.get_subclass_by_kind(design_kind)().generate()


def dump_template(template: TemplateDescriptor) -> None:
    """Save template to the disc"""

    def write_file(filepath: Path, content: str):
        with filepath.open("w") as f:
            f.write(content)

    filepath = Path(template.filename)
    utils.write_file_aware_existance(
        filepath,
        lambda: write_file(filepath, template.content),
    )


class _DesignTemplate(ABC):
    """Generic template"""

    @abstractmethod
    def generate(self, **kwargs) -> List[TemplateDescriptor]:
        """Generate design template files"""
        raise NotImplementedError

    @abstractclassmethod
    def get_kind(cls) -> DesignKind:
        """Get kind of the template"""
        raise NotImplementedError

    def _read_template_file(self, filename: str) -> str:
        """Read provided template file"""
        with Path(__file__).parent.joinpath(filename).open("r") as f:
            return f.read()

    @classmethod
    def get_subclass_by_kind(cls, design_kind: DesignKind) -> Type[_DesignTemplate]:
        """Get template class according to design kind"""
        for cls in _DesignTemplate.__subclasses__():
            if cls.get_kind() == design_kind:
                return cls
        raise ValueError(f"Can't find template class for design_kind={design_kind}")


class _Verilog(_DesignTemplate):
    """Verilog design template"""

    def generate(self, **kwargs) -> List[TemplateDescriptor]:
        """Generate design template files"""
        content = self._read_template_file("tb.v")
        return [TemplateDescriptor("tb.v", content)]

    @classmethod
    def get_kind(cls) -> DesignKind:
        """Get kind of the template"""
        return DesignKind.verilog


class _SystemVerilog(_DesignTemplate):
    """SystemVerilog design template"""

    def generate(self, **kwargs) -> List[TemplateDescriptor]:
        """Generate design template files"""
        content = self._read_template_file("tb.sv")
        return [TemplateDescriptor("tb.sv", content)]

    @classmethod
    def get_kind(cls) -> DesignKind:
        """Get kind of the template"""
        return DesignKind.systemverilog