"""ANSI terminal operations kept separate from maze drawing decisions."""

import os
import sys

from .colors import RGBColor

ScreenPosition = tuple[int, int]  # Terminal coordinates are one-based.
ANSI_RESET = "\x1b[0m"


class Terminal:
    """Write text and colors at absolute terminal positions."""

    def require_size(self, columns: int, rows: int) -> None:
        """Require an interactive terminal with enough room for the display."""
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise ValueError("An interactive terminal is required for display")
        size = os.get_terminal_size(sys.stdout.fileno())
        if size.columns < columns or size.lines < rows:
            raise ValueError(
                f"Maze requires {columns} columns × {rows} rows, "
                f"but the terminal has {size.columns} columns × "
                f"{size.lines} rows. Zoom out or enlarge the terminal."
            )

    def clear(self) -> None:
        """Clear the screen and establish the top-left drawing origin."""
        print(end="\x1b[2J\x1b[H")

    def move_cursor(self, position: ScreenPosition) -> None:
        """Move to a one-based (row, column) screen position."""
        row, column = position
        print(end=f"\x1b[{row};{column}H")

    def set_color(self, *colors: int | RGBColor) -> None:
        """Apply named or true-color foreground/background ANSI codes."""
        codes = ";".join(str(color) for color in colors)
        print(end=f"\x1b[{codes}m")

    def write(self, text: str) -> None:
        """Write without appending a newline."""
        print(end=text)

    def reset_color(self) -> None:
        """Restore terminal colors even if drawing failed."""
        print(end=ANSI_RESET, flush=True)
