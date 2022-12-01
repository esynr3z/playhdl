import argparse
from pathlib import Path

from . import log
from . import utils
from . import tools
from . import settings

app_dir = Path.home().joinpath(".playhdl")
user_settings_file = app_dir.joinpath("settings.json")


def cmd_run(args: argparse.Namespace) -> None:
    """Invoke simulation in the current workspace"""
    log.debug(f"Execute 'cmd_run' with {args}")


def cmd_init(args: argparse.Namespace) -> None:
    """Initialize workspace in the current folder"""
    log.debug(f"Execute 'cmd_init' with {args}")


def cmd_setup(args: argparse.Namespace) -> None:
    """Setup configuration file with avaliable EDA"""
    log.debug(f"Execute 'cmd_setup' with {args}")
    try:
        settings.setup_user(app_dir, user_settings_file)
    except FileExistsError as e:
        log.warning(e.args[0])  # Warn user with provided message
        if utils.input_query_yes_no():
            e.args[1]()  # Call lambda with a dump method


def parse_args():
    """Parse CLI arguments"""
    parser_descr = """avaliable commands:
    setup - setup configuration file with avaliable EDA
    init  - initialize workspace in the current folder
    run   - invoke simulation in the current workspace

add -h/--help argument to any command to get more information"""
    parser = argparse.ArgumentParser(
        description=parser_descr,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = parser.add_subparsers(help="command to process", dest="command", required=True)

    parser_setup = subparsers.add_parser("setup")
    parser_setup.set_defaults(func=cmd_setup)

    parser_init = subparsers.add_parser("init")
    parser_init.add_argument("mode", help="design and testbench mode")
    parser_init.set_defaults(func=cmd_init)

    parser_run = subparsers.add_parser("run")
    parser_run.add_argument("tool", help="tool for simulation")
    parser_run.add_argument("--waves", action="store_true", help="open waves in the simulation end")
    parser_run.add_argument("--time", type=int, help="total simulation time")
    parser_run.set_defaults(func=cmd_run)

    return parser.parse_args()


def main():
    """Entry point to CLI of the application"""
    log.init_logger()
    args = parse_args()
    args.func(args)
