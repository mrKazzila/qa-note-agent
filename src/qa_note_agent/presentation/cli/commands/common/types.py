__all__ = ("CLICommandFunc",)

from collections.abc import Callable
from typing import Any

CLICommandFunc = Callable[..., Any]
