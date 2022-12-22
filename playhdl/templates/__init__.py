from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Type

from .. import log, utils

_logger = log.get_logger()


class DesignKind(utils.ExtendedEnum):
    verilog = enum.auto()
    sv = enum.auto()
    sv_uvm12 = enum.auto()
    vhdl = enum.auto()


@dataclass
class TemplateDescriptor:
    filename: str
    content: str


def generate(design_kind: DesignKind) -> List[TemplateDescriptor]:
    """Get template files according to design kind"""
    _logger.info(f"Generate templates for '{design_kind}' design ...")
    templates = _DesignTemplate.get_subclass_by_kind(design_kind)().generate()
    filenames = [t.filename for t in templates]
    _logger.info(f"  {' '.join(filenames)}")
    return templates


def dump(template: TemplateDescriptor, **kwargs: Any) -> None:
    """Save template to a disc"""
    filepath = Path(template.filename)
    _logger.info(f"Save '{filepath}' to a disk ...")
    if utils.is_write_allowed(filepath, bool(kwargs.get("query_force_yes", False))):
        with filepath.open("w") as f:
            f.write(template.content)


class _DesignTemplate(ABC):
    """Generic template"""

    def generate(self, **kwargs: Any) -> List[TemplateDescriptor]:
        """Generate design template files"""
        content = self._read_template_file(self.get_template_name())
        return [TemplateDescriptor(self.get_template_name(), content)]

    @classmethod
    @abstractmethod
    def get_kind(cls) -> DesignKind:
        """Get kind of the template"""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_template_name(cls) -> str:
        """Get name of the template"""
        raise NotImplementedError

    def _read_template_file(self, filename: str) -> str:
        """Read provided template file"""
        with Path(__file__).parent.joinpath(filename).open("r") as f:
            return f.read()

    @classmethod
    def get_subclass_by_kind(cls, design_kind: DesignKind) -> Type[_DesignTemplate]:
        """Get template class according to design kind"""
        for cls in _DesignTemplate.__subclasses__():  # type: ignore
            if cls.get_kind() == design_kind:
                return cls
        raise ValueError(f"Can't find template class for design_kind={design_kind}")


class _Verilog(_DesignTemplate):
    """Verilog design template"""

    @classmethod
    def get_kind(cls) -> DesignKind:
        return DesignKind.verilog

    @classmethod
    def get_template_name(cls) -> str:
        return "tb.v"


class _SystemVerilog(_DesignTemplate):
    """SystemVerilog design template"""

    @classmethod
    def get_kind(cls) -> DesignKind:
        """Get kind of the template"""
        return DesignKind.sv

    @classmethod
    def get_template_name(cls) -> str:
        return "tb.sv"


class _SystemVerilogUvm12(_DesignTemplate):
    """SystemVerilog UVM 1.2 design template"""

    @classmethod
    def get_kind(cls) -> DesignKind:
        return DesignKind.sv_uvm12

    @classmethod
    def get_template_name(cls) -> str:
        return "tb_uvm12.sv"
