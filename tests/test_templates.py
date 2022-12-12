"""Tests for playhdl/templates/__init__.py
"""

import pytest
from io import StringIO

from playhdl.templates import *
import playhdl.templates as templates


class TestGenerate:
    def test_verilog(self):
        descr: List[TemplateDescriptor] = generate(DesignKind.verilog)
        assert len(descr) == 1
        assert descr[0].filename.endswith(".v")
        assert "module tb;" in descr[0].content
        assert "endmodule" in descr[0].content

    def test_sv(self):
        descr: List[TemplateDescriptor] = generate(DesignKind.sv)
        assert len(descr) == 1
        assert descr[0].filename.endswith(".sv")
        assert "module tb;" in descr[0].content
        assert "bit clk" in descr[0].content
        assert "endmodule" in descr[0].content

    def test_sv_uvm12(self):
        descr: List[TemplateDescriptor] = generate(DesignKind.sv_uvm12)
        assert len(descr) == 1
        assert descr[0].filename.endswith(".sv")
        assert "module tb;" in descr[0].content
        assert "import uvm_pkg::*;" in descr[0].content
        assert "endmodule" in descr[0].content

    def test_vhdl(self):
        with pytest.raises(ValueError):
            generate(DesignKind.vhdl)


class TestDump:
    @pytest.fixture
    def descr(self, tmp_path: Path) -> TemplateDescriptor:
        return TemplateDescriptor(filename=str(tmp_path.joinpath("test")), content="The answer is\n42\n")

    @pytest.fixture
    def descr_alt(self, tmp_path: Path) -> TemplateDescriptor:
        return TemplateDescriptor(filename=str(tmp_path.joinpath("test")), content="Cake is a lie!\n")

    def read_file(self, file) -> str:
        with file.open("r") as f:
            return f.read()

    def test_dump_not_exist(self, descr):
        dump(descr)
        filepath = Path(descr.filename)
        assert filepath.is_file() is True
        assert descr.content == self.read_file(filepath)

    def test_dump_exist_query_yes(self, descr, descr_alt, monkeypatch):
        monkeypatch.setattr("sys.stdin", StringIO("a\nc\ny"))
        dump(descr)
        dump(descr_alt)
        filepath = Path(descr_alt.filename)
        assert filepath.is_file() is True
        assert descr_alt.content == self.read_file(filepath)

    def test_dump_exist_query_no(self, descr, descr_alt, monkeypatch):
        monkeypatch.setattr("sys.stdin", StringIO("a\nc\nn"))
        dump(descr)
        dump(descr_alt)
        filepath = Path(descr_alt.filename)
        assert filepath.is_file() is True
        assert descr.content == self.read_file(filepath)

    def test_dump_exist_query_force_yes(self, descr, descr_alt, monkeypatch):
        monkeypatch.setattr("sys.stdin", StringIO("a\nc\nn"))
        dump(descr)
        dump(descr_alt, query_force_yes=True)
        filepath = Path(descr_alt.filename)
        assert filepath.is_file() is True
        assert descr_alt.content == self.read_file(filepath)


class TestDesignTemplate:
    def test_abc(self):
        with pytest.raises(NotImplementedError):
            templates._DesignTemplate.get_kind()
        with pytest.raises(NotImplementedError):
            templates._DesignTemplate.get_template_name()
        with pytest.raises(TypeError):
            templates._DesignTemplate()
