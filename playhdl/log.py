import os

import rich

from . import utils


def debug(*args, **kwargs) -> None:
    if utils.is_debug_en():
        rich.print("[bold green]DEBUG:[/bold green] ", *args, **kwargs)


def info(*args, **kwargs) -> None:
    rich.print(*args, **kwargs)


def warning(*args, **kwargs) -> None:
    rich.print("[bold yellow]WARNING:[/bold yellow] ", *args, **kwargs)


def error(*args, **kwargs) -> None:
    rich.print("[bold red]ERROR:[/bold red] ", *args, **kwargs)
