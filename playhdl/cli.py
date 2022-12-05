import argparse
from pathlib import Path

from . import log
from . import utils
from . import templates
from . import tools
from . import project
from . import settings
from . import runner

logger = log.get_logger()

app_dir = Path.home().joinpath(".playhdl")
user_settings_file = app_dir.joinpath("settings.json")
project_file = Path("playhdl.json")


def _load_settings(settings_file: Path) -> settings.UserSettings:
    """Load user settings"""
    try:
        return settings.load(settings_file)
    except FileNotFoundError:
        logger.error(f"Settings file '{settings_file}' was not found. Run 'setup' command to create it first.")
        exit(1)


def _load_project(project_file: Path) -> project.Project:
    """Load project"""
    try:
        return project.load(project_file)
    except FileNotFoundError:
        logger.error(f"Project file '{project_file}' was not found. Run 'init' command to create it first.")
        exit(1)


def cmd_run(args: argparse.Namespace) -> None:
    """Invoke simulation in the current workspace"""
    logger.debug(f"Execute 'cmd_run' with {args}")

    # Load user settings
    user_settings = _load_settings(user_settings_file)

    # Load project
    project = _load_project(project_file)

    # Run simulator
    try:
        runner.run(project, user_settings, args.tool, args.waves)
    except (ValueError, RuntimeError) as e:
        logger.error(str(e))
        exit(1)


def cmd_init(args: argparse.Namespace) -> None:
    """Initialize workspace in the current folder"""
    logger.debug(f"Execute 'cmd_init' with {args}")

    # Load user settings
    user_settings = _load_settings(user_settings_file)

    # Generate code templates
    source_files = templates.generate_templates(args.mode)
    for src in source_files:
        with utils.query_if_file_exists(args.query_force_yes):
            templates.dump_template(src)

    # Init project file
    with utils.query_if_file_exists(args.query_force_yes):
        try:
            project.init(project_file, args.mode, [f.filename for f in source_files], user_settings)
        except ValueError as e:
            logger.error(str(e))
            exit(1)


def cmd_setup(args: argparse.Namespace) -> None:
    """Setup configuration file with avaliable EDA"""
    logger.debug(f"Execute 'cmd_setup' with {args}")
    with utils.query_if_file_exists(args.query_force_yes):
        settings.setup_user(app_dir, user_settings_file)


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
    parser.add_argument("-y", dest="query_force_yes", action="store_true", help="answer 'yes' to all queries")

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
    parser_run.add_argument("tool", type=tools.ToolUid, help="tool for simulation")
    parser_run.add_argument("--waves", action="store_true", help="open waves after simulation ends")
    parser_run.set_defaults(func=cmd_run)

    return parser.parse_args()


def main():
    """Entry point to CLI of the application"""
    log.init_logger()
    args = parse_args()
    args.func(args)
