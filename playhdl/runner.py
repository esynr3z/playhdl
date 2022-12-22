from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, TYPE_CHECKING

from . import log, project, settings

if TYPE_CHECKING:
    from . import tools

_logger = log.get_logger()


def _patch_path(bin_dir: Path, env: Dict[str, str]) -> None:
    """Patch PATH variable inplace"""
    env_path = f"{bin_dir}:{env.get('PATH', '')}"
    env.setdefault("PATH", env_path)


def _prepare_work_dir(tool_uid: tools.ToolUid) -> Path:
    """Prepare working directory"""
    work_dir = Path(f"./{tool_uid}")
    _logger.info(f"Clear working directory '{work_dir}'")
    shutil.rmtree(work_dir, ignore_errors=True)
    work_dir.mkdir()
    return work_dir


def _exec(cmd: str, cwd: Path, bin_dir: Path, env: Dict[str, str]) -> None:
    """Execute system process"""
    if not cmd:
        _logger.warning("Command is empty. Nothing to do.")
        return

    # Prepare environment
    proc_env = os.environ.copy()
    proc_env.update(env)
    _patch_path(bin_dir, proc_env)

    # Run process
    kwargs = {
        "args": cmd,
        "cwd": cwd,
        "env": os.environ.copy(),
        "stdout": sys.stdout,
        "stderr": subprocess.STDOUT,
        "shell": True,
    }
    proc = subprocess.run(**kwargs)  # type: ignore
    if proc.returncode != 0:
        raise RuntimeError(f"Command '{cmd}' returned {proc.returncode}. Check the output above for diagnostics.")


def run(project: project.Project, settings: settings.UserSettings, tool_uid: tools.ToolUid, waves: bool) -> None:
    # Check that provided tool exists
    if tool_uid not in project.tools.keys():
        raise ValueError(
            f"Tool '{tool_uid}' was not found in your project file. Available tools: {list(project.tools.keys())}."
            " Check your global settings and project file, then run again."
        )

    # Prepare tool attributes
    tool_settings = settings.tools[tool_uid]
    tool_script = project.tools[tool_uid]
    work_dir = _prepare_work_dir(tool_uid)

    # Run tool
    _logger.info("Run compilation ...")
    for cmd in tool_script.build:
        _logger.info(f"  {cmd}")
        _exec(cmd=cmd, cwd=work_dir, bin_dir=tool_settings.bin_dir, env=tool_settings.env)

    _logger.info("Run simulation ...")
    for cmd in tool_script.sim:
        _logger.info(f"  {cmd}")
        _exec(cmd=cmd, cwd=work_dir, bin_dir=tool_settings.bin_dir, env=tool_settings.env)

    if waves:
        _logger.info("Show waves ...")
        for cmd in tool_script.waves:
            _logger.info(f"  {cmd}")
            _exec(cmd=cmd, cwd=work_dir, bin_dir=tool_settings.bin_dir, env=tool_settings.env)
