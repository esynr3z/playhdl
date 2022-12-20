import argparse
from pathlib import Path

from . import log, project, runner, settings, templates, tools, utils

_logger = log.get_logger()

app_dir = Path.home().joinpath(".playhdl")
user_settings_file = app_dir.joinpath("settings.json")
project_file = Path("playhdl.json")


def _load_settings(settings_file: Path) -> settings.UserSettings:
    """Load user settings"""
    try:
        return settings.load(settings_file)
    except FileNotFoundError:
        _logger.error(f"Settings file '{settings_file}' was not found. Run 'setup' command to create it first.")
        exit(1)


def _load_project(project_file: Path) -> project.Project:
    """Load project"""
    try:
        return project.load(project_file)
    except FileNotFoundError:
        _logger.error(f"Project file '{project_file}' was not found. Run 'init' command to create it first.")
        exit(1)


def _show_run_options(project_descriptor: project.Project) -> None:
    """Show run options"""
    _logger.info("You can run simulation using one of the options below:")
    for uid in project_descriptor.tools:
        _logger.info(f"  playhdl run {uid}")


def cmd_run(args: argparse.Namespace) -> None:
    """Invoke simulation in the current workspace"""
    _logger.debug(f"Execute 'cmd_run' with {args}")

    # Load user settings
    user_settings = _load_settings(user_settings_file)

    # Load project
    project_descriptor = _load_project(project_file)

    if not args.tool:
        _show_run_options(project_descriptor)
        exit(1)

    # Run simulator
    try:
        runner.run(project_descriptor, user_settings, args.tool, args.waves)
    except (ValueError, RuntimeError, FileNotFoundError) as e:
        _logger.error(str(e))
        exit(1)


def _show_init_options() -> None:
    """Show init options"""
    _logger.info("You can initialize project using one of the options below:")
    for kind in templates.DesignKind:
        _logger.info(f"  playhdl init {kind}")


def cmd_init(args: argparse.Namespace) -> None:
    """Initialize workspace in the current folder"""
    _logger.debug(f"Execute 'cmd_init' with {args}")

    if not args.mode:
        _show_init_options()
        exit(1)

    # Load user settings
    user_settings = _load_settings(user_settings_file)

    # Generate code templates
    source_files = templates.generate(args.mode)
    for src in source_files:
        templates.dump(src, query_force_yes=args.query_force_yes)

    # Init project file
    try:
        project_descriptor = project.create(project_file, args.mode, [f.filename for f in source_files], user_settings)
        _logger.info(f"Save project file to '{project_file}' ...")
        project.dump(project_file, project_descriptor, query_force_yes=args.query_force_yes)
    except ValueError as e:
        _logger.error(str(e))
        exit(1)

    # Show run options
    project_descriptor = _load_project(project_file)
    _show_run_options(project_descriptor)


def cmd_setup(args: argparse.Namespace) -> None:
    """Setup configuration file with avaliable EDA"""
    _logger.debug(f"Execute 'cmd_setup' with {args}")
    settings.setup(app_dir, user_settings_file, query_force_yes=args.query_force_yes)


def cmd_info(args: argparse.Namespace) -> None:
    """Print information about tools and configuration"""
    _logger.debug(f"Execute 'cmd_info' with {args}")
    user_settings = _load_settings(user_settings_file)

    available_tools = []
    for uid, tool_settings in user_settings.tools.items():
        available_tools.append(f"{uid:>15}: {tool_settings.bin_dir}")
    newline = "\n"  # f-string expression part cannot include a backslash
    _logger.info(f"Tools available:\n{newline.join(available_tools)}")
    _logger.info(f"Tools compatibility table:\n{tools.get_compatibility_text_table()}")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments"""
    parser_descr = f"""playhdl {utils.get_pkg_version()}
avaliable commands:
    setup - setup configuration file with avaliable EDA
    init  - initialize workspace in the current folder
    run   - invoke simulation in the current workspace
    info  - print information about tools and configuration

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
        "mode",
        nargs="?",
        type=templates.DesignKind,
        choices=list(templates.DesignKind),
        help="design and testbench mode",
    )
    parser_init.set_defaults(func=cmd_init)

    parser_run = subparsers.add_parser("run")
    parser_run.add_argument("tool", nargs="?", type=tools.ToolUid, help="tool for simulation")
    parser_run.add_argument("--waves", action="store_true", help="open waves after simulation ends")
    parser_run.set_defaults(func=cmd_run)

    parser_setup = subparsers.add_parser("info")
    parser_setup.set_defaults(func=cmd_info)

    return parser.parse_args()


def main() -> None:
    """Entry point to CLI of the application"""
    log.init_logger()
    args = parse_args()
    args.func(args)
