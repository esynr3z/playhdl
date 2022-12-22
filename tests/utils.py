import subprocess
import sys
from dataclasses import dataclass
from typing import Any


@dataclass
class ProcessResult:
    returncode: int
    stdout: str
    stderr: str


def shell(cmd: str, **kwargs: Any) -> ProcessResult:
    """Execute command and return convenient dataclass"""
    proc = subprocess.run(cmd, shell=True, capture_output=True, **kwargs)

    return ProcessResult(
        returncode=proc.returncode,
        stdout=proc.stdout.decode(),  # type: ignore
        stderr=proc.stderr.decode(),  # type: ignore
    )


class OverrideSysArgv:
    """Context manager to temporarily override sys.argv"""

    def __init__(self, *new_args: Any) -> None:
        self._orig_argv = sys.argv
        self.args = type(self._orig_argv)(new_args)

    def __enter__(self) -> None:
        sys.argv = self.args

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        sys.argv = self._orig_argv
