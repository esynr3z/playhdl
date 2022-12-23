# playhdl

[![Tests & Checks](https://github.com/esynr3z/playhdl/actions/workflows/test.yml/badge.svg)](https://github.com/esynr3z/playhdl/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/playhdl.svg)](https://badge.fury.io/py/playhdl)

You can think about `playhdl` as [EdaPlayground](https://edaplayground.com/), but which is CLI-based and uses simulators on your local machine.

It gives you ability to simulate tiny snippets of HDL code in several commands without any headache related to vast tool guides, command-line arguments and etc.:

```sh
playhdl init sv
playhdl run modelsim
```

## Features

`playhdl` is written in pure Python without any external dependencies, so it is easy to use it in any environment (laptop, server, etc.), where Python 3.8+ is available.

It supports various project types (HDL languages + libraries) and many simulators:

|               |    verilog         |      sv            |   sv_uvm12         |     vhdl      |
| ------------- | :----------------: | :----------------: | :----------------: | :-----------: |
| [modelsim](https://eda.sw.siemens.com/en-US/ic/modelsim/) | :heavy_check_mark: | :heavy_check_mark: | | |
| [xcelium](https://www.cadence.com/ko_KR/home/tools/system-design-and-verification/simulation-and-testbench-verification/xcelium-simulator.html) | :heavy_check_mark: | :heavy_check_mark: | | |
| [verilator](https://www.veripool.org/verilator/) | :heavy_check_mark: | :heavy_check_mark: | | |
| [icarus](http://iverilog.icarus.com/) | :heavy_check_mark: | :heavy_check_mark: | | |
| [vcs](https://www.synopsys.com/verification/simulation/vcs.html) | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | |
| [vivado](https://www.xilinx.com/products/design-tools/vivado.html) | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | |

## Quick start

* Install the latest stable release (Python 3.8+ is required):

```sh
python -m pip install -U playhdl
```

* Setup settings file `$HOME/.playhdl/settings.json` with a list of all automatically-discoverd simulators. Edit file manually to add undiscovered ones. This have to be done only once.

```sh
playhdl setup
```

* Initialize project file `playhdl.json` and template testbench in the current directory. Project file contains specific commands to be executed for compilation and simulation processes. Edit it manually to tweak tool arguments if required.

```sh
playhdl init sv # this will create ready-to-simulate tb.sv
```

* Run simulation in one of the supported simulators for this project (language):

```sh
playhdl run icarus
# to open waves after simulation
playhdl run icarus --waves
```

## Tool command guide

To get general help and command list:

```sh
playhdl -h
```

To get help about specific command

```sh
playhdl <command> -h
```

### `setup` command

Settings of the tool are stored in the JSON file under `$HOME/.playhdl` directory.

To create `$HOME/.playhdl/settings.json` run

```sh
playhdl setup
```

It will try to find all supported simulators and fill the json. If you have multiple versions of simulators or some of them were not found, add them manually to your settings file.

Settings file structure:

```json
{
    "tools": {
        "<tool_uid>": {
            "kind": "<tool_kind>",
            "bin_dir": "<path_to_bin>",
            "env": {},
            "extras": {}
        }
    }
}
```

All tools settings are located in a dictionary under `"tools"` key.

Every tool has it is own `tool_uid`, which is just a string with any unique name, e.g. `"modelsim"`, `"verilator5"`, `"my_secret_simulator"`.

Valid `"kind"` must be provided:

* `"modelsim"`
* `"xcelium"`
* `"verilator"`
* `"icarus"`
* `"vcs"`
* `"vivado"`

Other fields:

* `"bin_dir"` - a string with a path to a directory with executable files
* `"env"` - a dictionary with additional enviroment variables (keys and values are strings)
* `"extras"` - a dictionary with extra values for a specific simulator kind

Extras for `"vcs"` kind:

* `"gui"` - `"verdi"` or `"dve"` select default GUI for VCS

### `init` command

This command creates JSON project file `playhdl.json` and HDL testbench in the current directory.

```sh
playhdl init <mode>
```

Where `<mode>` is one of the supported project modes:

* `verilog` - Verilog-2001
* `sv` - SystemVerilog-2017
* `sv_uvm12` - SystemVerilog-2017 + UVM 1.2
* `vhdl` - VHDL-93

Project file is filled with scripts for all suitable simulators for the selected mode. It's internal structure:

```json
{
    "tools": {
        "<tool_uid>": {
            "build": [
                "<cmd0>",
                "<cmd1>",
                "<cmd2>"
            ],
            "sim": [
                "<cmd>"
            ],
            "waves": [
                "<cmd>"
            ]
        }
    }
}
```

There are three categories of commands:

* `"build"` - commands needed to compile and elaborate sources
* `"sim"` - commands needed to run simulation
* `"waves"` - commands needed to open waves for analysis

Any command can be customized for specific needs.

### `run` command

This command runs CLI-mode simulation in a specific simulator according to project file

```sh
playhdl run <tool_uid>
```

Argument `--waves` can be added to open waves for analysis after simulation ends

```sh
playhdl run <tool_uid> --waves
```

### `info` command

This command just prints some useful information:

* all tools specified in your settings file
* current compatibility table between project mode and simulator

```sh
playhdl info
```

## Developer guide

Install `poetry`

```sh
python -m pip install -U poetry
```

Setup virtual environment

```sh
make setup-dev
```

You can specify Python version to use

```sh
make setup-dev PYTHON_VERSION=3.9
```

To run `playhdl` from sources

```sh
poetry run playhdl <args>
```

`Makefile` provides additional ways to interact with project:

* `make format` - auto-format all sources
* `make check-format` - check current formatting of sources
* `make lint` - perform linting
* `make type` - perform type checking
* `make test` - run all tests
* `make pre-commit` - shorthand for combination of `check-format`, `lint`, `type`, `test`

## Miscellaneous

### Offline install

For an offline install you have several options of how to get `wheel`:

* build locally using [poetry](https://python-poetry.org/)

```sh
python -m pip install -U poetry
poetry build
```

* download `.whl` from [PyPi](https://pypi.org/)

```sh
python -m pip download playhdl
```

Then you can use pip to install it on an offline machine:

```sh
python -m pip install <wheel_file_name>.whl
```
