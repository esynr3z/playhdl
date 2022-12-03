import argparse
from pathlib import Path

from . import log
from . import utils
from . import templates
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

    # Generate code templates
    source_files = templates.generate_templates(args.mode)
    source_filenames = [f.filename for f in source_files]

    # Generate simulator scripts
    tool_scripts = tools.generate_all_possible_scripts(args.mode, source_filenames)
    if len(tool_scripts) == 0:
        log.error(f"Can't find any suitable tool for the provided design mode '{args.mode}'")
        exit(1)


def cmd_setup(args: argparse.Namespace) -> None:
    """Setup configuration file with avaliable EDA"""
    log.debug(f"Execute 'cmd_setup' with {args}")
    utils.execute_with_file_exists_query(
        lambda: settings.setup_user(app_dir, user_settings_file),
    )


def parse_args():
    """Parse CLI arguments"""
    parser_descr = """avaliable commands:
    setup - setup configuration file with avaliable EDA
    init  - initialize workspace in the current folder
    run   - invoke simulation in the current workspace

add -h/--help argument to any command to get more information"""

    class CustomFormatter(
        argparse.RawTextHelpFormatter,
        argparse.ArgumentDefaultsHelpFormatter,
    ):
        pass

    parser = argparse.ArgumentParser(
        description=parser_descr,
        formatter_class=CustomFormatter,
    )

    subparsers = parser.add_subparsers(help="command to process", dest="command", required=True)

    parser_setup = subparsers.add_parser("setup")
    parser_setup.set_defaults(func=cmd_setup)

    parser_init = subparsers.add_parser("init", formatter_class=CustomFormatter)
    parser_init.add_argument(
        "--mode",
        type=templates.DesignKind,
        default=templates.DesignKind.systemverilog,
        choices=list(templates.DesignKind),
        help="design and testbench mode",
    )
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
