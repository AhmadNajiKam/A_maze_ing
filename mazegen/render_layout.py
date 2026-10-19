"""Translate maze cells and passages into terminal drawing coordinates."""

from .directions import Direction
from .menu import main_menu


class RenderLayout:
    """Describe a maze drawn at the top-left of the terminal."""

    def __init__(self, width: int, height: int) -> None:
        """Own drawing dimensions and margins for one maze."""
        self.width = width
        self.height = height
        self.cell_column_spacing = 3
        self.cell_row_spacing = 2
        self.cell_interior_width = self.cell_column_spacing - 1
        self._border_thickness = 1
        self._menu_extra_rows = 3
        self._terminal_wrap_margin = 1

    @property
    def drawing_columns(self) -> int:
        """Include the final right-hand border column."""
        return self.width * self.cell_column_spacing + self._border_thickness

    @property
    def drawing_rows(self) -> int:
        """Include the final bottom border row."""
        return self.height * self.cell_row_spacing + self._border_thickness

    @property
    def required_columns(self) -> int:
        """Allow for both drawing/menu width and terminal line wrapping."""
        options, prompt = main_menu()
        menu_columns = max(len(prompt), *(len(option) for option in options))
        return (max(self.drawing_columns, menu_columns)
                + self._terminal_wrap_margin)

    @property
    def required_rows(self) -> int:
        """Fit the maze, menu, prompt, and feedback space."""
        options, _ = main_menu()
        return (self.drawing_rows + len(options)
                + 1 + self._menu_extra_rows)

    @property
    def menu_position(self) -> tuple[int, int]:
        """Place menu output on the first line below the maze."""
        return self.drawing_rows + 1, 1

    def cell_corner(self, cell: tuple[int, int]) -> tuple[int, int]:
        """Locate a cell's top-left junction on the zero-based canvas."""
        row, column = cell
        return row * self.cell_row_spacing, column * self.cell_column_spacing

    def cell_interior(self, cell: tuple[int, int]) -> tuple[int, int]:
        """Return the first interior character in terminal coordinates."""
        row, column = self.cell_corner(cell)
        return (row + self._border_thickness + 1,
                column + self._border_thickness + 1)

    def passage(
        self, cell: tuple[int, int], direction: Direction,
    ) -> tuple[int, int]:
        """Locate the shared passage when stepping out of a cell."""
        row, column = self.cell_interior(cell)
        if direction.row_offset:
            return row + direction.row_offset, column
        if direction.column_offset > 0:
            return row, column + self.cell_interior_width
        return row, column - self._border_thickness
