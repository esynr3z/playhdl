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

You can get an up-to-date table using a command below:

```sh
playhdl info
```

## Quick start

### Install

To install the latest stable release (Python 3.8+ is required):

```sh
python -m pip install -U playhdl
```

### Setup simulators

### Create project

### Run simulation

## Command guide

### setup

### init

### run

### info
