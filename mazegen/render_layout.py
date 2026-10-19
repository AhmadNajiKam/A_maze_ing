"""Translate maze cells and passages into terminal drawing coordinates."""

from dataclasses import dataclass

from .directions import Cell, Direction
from .menu import MENU_OPTIONS, MENU_PROMPT
from .terminal import ScreenPosition

CELL_COLUMN_SPACING = 3
CELL_ROW_SPACING = 2
CELL_INTERIOR_WIDTH = CELL_COLUMN_SPACING - 1
BORDER_THICKNESS = 1
# Leave room for validation messages and a small gap below the menu.
MENU_EXTRA_ROWS = 3
TERMINAL_WRAP_MARGIN = 1


@dataclass(frozen=True)
class RenderLayout:
    """Describe a maze drawn at the top-left of the terminal."""

    width: int
    height: int

    @property
    def drawing_columns(self) -> int:
        """Include the final right-hand border column."""
        return self.width * CELL_COLUMN_SPACING + BORDER_THICKNESS

    @property
    def drawing_rows(self) -> int:
        """Include the final bottom border row."""
        return self.height * CELL_ROW_SPACING + BORDER_THICKNESS

    @property
    def required_columns(self) -> int:
        """Allow for both drawing/menu width and terminal line wrapping."""
        menu_columns = max(len(MENU_PROMPT),
                           *(len(option) for option in MENU_OPTIONS))
        return max(self.drawing_columns, menu_columns) + TERMINAL_WRAP_MARGIN

    @property
    def required_rows(self) -> int:
        """Fit the maze, menu, prompt, and feedback space."""
        return (self.drawing_rows + len(MENU_OPTIONS)
                + 1 + MENU_EXTRA_ROWS)

    @property
    def menu_position(self) -> ScreenPosition:
        """Place menu output on the first line below the maze."""
        return self.drawing_rows + 1, 1

    def cell_corner(self, cell: Cell) -> tuple[int, int]:
        """Locate a cell's top-left junction on the zero-based canvas."""
        row, column = cell
        return row * CELL_ROW_SPACING, column * CELL_COLUMN_SPACING

    def cell_interior(self, cell: Cell) -> ScreenPosition:
        """Return the first interior character in terminal coordinates."""
        row, column = self.cell_corner(cell)
        return row + BORDER_THICKNESS + 1, column + BORDER_THICKNESS + 1

    def passage(self, cell: Cell, direction: Direction) -> ScreenPosition:
        """Locate the shared passage when stepping out of a cell."""
        row, column = self.cell_interior(cell)
        if direction.row_offset:
            return row + direction.row_offset, column
        if direction.column_offset > 0:
            return row, column + CELL_INTERIOR_WIDTH
        return row, column - BORDER_THICKNESS
