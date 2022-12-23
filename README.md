# playhdl

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
playhdl sv # this will create ready-to-simulate tb.sv
```

* Run simulation in one of the supported simulators for this project (language):

```sh
playhdl run icarus
# to open waves after simulation
playhdl run icarus --waves
```

## Offline install

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
        <tool_uid>: {
            "kind": <tool_kind>,
            "bin_dir": <path_to_bin>,
            "env": {},
            "extras": {}
        }
    }
}
```

All tools settings are located in dictionary under `"tools"` key.

Every tool has it is own `tool_uid`, which is just string with any unique name, e.g. `"modelsim"`, `"verilator5"`, `"my_secret_simulator"`.

Valid `"kind"` must be provided:

* `"modelsim"`
* `"xcelium"`
* `"verilator"`
* `"icarus"`
* `"vcs"`
* `"vivado"`

Other fields:

* `"bin_dir"` - string with path to directory with executable files
* `"env"` - dictionary with additional enviroment variables (keys and values are strings)
* `"extras"` - dictionary with extra values for specific simulator kind

Extras for `"vcs"` kind:

* `"gui"` - `"verdi"` or `"dve"` select default GUI for VCS

### `init` command

### `run` command

### `info` command

## Developer guide
