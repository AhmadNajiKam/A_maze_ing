"""Draw Unicode walls and colored overlays using a shared terminal layout."""

from dataclasses import dataclass
from enum import IntFlag

from .colors import BackgroundColor, ForegroundColor, RGBColor
from .directions import Wall, make_directions
from .grid import MazeGrid
from .render_layout import RenderLayout
from .terminal import Terminal


class Junction(IntFlag):
    """Line segments meeting at a junction, independent of cell wall bits."""

    NONE = 0
    UP = 1
    RIGHT = 2
    DOWN = 4
    LEFT = 8


@dataclass
class DisplaySettings:
    """Keep user display preferences independent of a generated maze."""

    show_path: bool = False
    wall_color: int | RGBColor = ForegroundColor.WHITE
    path_color: int | RGBColor = BackgroundColor.CYAN
    pattern_color: int | RGBColor = BackgroundColor.WHITE


class Renderer:
    """Draw walls and overlays using (row, column) endpoints."""

    def __init__(
        self, maze: list[list[int]], solution: str = "", *,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] | None = None,
        settings: DisplaySettings | None = None,
        terminal: Terminal | None = None,
    ) -> None:
        """Accept reusable preferences and an injectable terminal writer."""
        self.settings = settings if settings is not None else DisplaySettings()
        self._terminal = terminal if terminal is not None else Terminal()
        self._directions_by_letter = {
            direction.letter: direction for direction in make_directions()
        }
        self._horizontal_line = "━"
        self._vertical_line = "┃"
        self._junction_glyphs = {
            Junction.NONE: " ",
            Junction.UP: "╹",
            Junction.RIGHT: "╺",
            Junction.UP | Junction.RIGHT: "┗",
            Junction.DOWN: "╻",
            Junction.UP | Junction.DOWN: "┃",
            Junction.RIGHT | Junction.DOWN: "┏",
            Junction.UP | Junction.RIGHT | Junction.DOWN: "┣",
            Junction.LEFT: "╸",
            Junction.UP | Junction.LEFT: "┛",
            Junction.RIGHT | Junction.LEFT: "━",
            Junction.UP | Junction.RIGHT | Junction.LEFT: "┻",
            Junction.DOWN | Junction.LEFT: "┓",
            Junction.UP | Junction.DOWN | Junction.LEFT: "┫",
            Junction.RIGHT | Junction.DOWN | Junction.LEFT: "┳",
            Junction.UP | Junction.RIGHT | Junction.DOWN | Junction.LEFT: "╋",
        }
        self.replace_maze(maze, solution, entry=entry, exit=exit)

    def replace_maze(
        self, maze: list[list[int]], solution: str, *,
        entry: tuple[int, int], exit: tuple[int, int] | None = None,
    ) -> None:
        """Replace maze content while retaining all display preferences."""
        self._grid = MazeGrid(maze)
        self._layout = RenderLayout(self._grid.width, self._grid.height)
        self._cell_interior = " " * self._layout.cell_interior_width
        self._solution = solution
        self._entry = entry
        self._exit = exit if exit is not None else (
            self._grid.height - 1, self._grid.width - 1,
        )

    def toggle_path(self) -> None:
        """Toggle the solution without hiding the endpoints."""
        self.settings.show_path = not self.settings.show_path

    def _build_wall_canvas(self) -> list[list[str]]:
        """Draw segments first, then join them at their intersections."""
        canvas = [[" "] * self._layout.drawing_columns
                  for _ in range(self._layout.drawing_rows)]
        for row in range(self._grid.height):
            for column in range(self._grid.width):
                cell = (row, column)
                top, left = self._layout.cell_corner(cell)
                bottom = top + self._layout.cell_row_spacing
                right = left + self._layout.cell_column_spacing
                horizontal_walls = ((Wall.NORTH, top), (Wall.SOUTH, bottom))
                for wall, wall_row in horizontal_walls:
                    if self._grid.has_wall(cell, wall):
                        for wall_column in range(left + 1, right):
                            canvas[wall_row][wall_column] = (
                                self._horizontal_line
                            )
                vertical_walls = ((Wall.WEST, left), (Wall.EAST, right))
                for wall, wall_column in vertical_walls:
                    if self._grid.has_wall(cell, wall):
                        for wall_row in range(top + 1, bottom):
                            canvas[wall_row][wall_column] = self._vertical_line
        for row in range(0, self._layout.drawing_rows,
                         self._layout.cell_row_spacing):
            for column in range(0, self._layout.drawing_columns,
                                self._layout.cell_column_spacing):
                canvas[row][column] = self._junction_glyph(
                    canvas, row, column,
                )
        return canvas

    def _junction_glyph(
        self, canvas: list[list[str]], row: int, column: int,
    ) -> str:
        """Combine line segments around this junction into a Unicode glyph."""
        segments = Junction.NONE
        if row > 0 and canvas[row - 1][column] == self._vertical_line:
            segments |= Junction.UP
        if (column + 1 < self._layout.drawing_columns
                and canvas[row][column + 1] == self._horizontal_line):
            segments |= Junction.RIGHT
        if (row + 1 < self._layout.drawing_rows
                and canvas[row + 1][column] == self._vertical_line):
            segments |= Junction.DOWN
        if column > 0 and canvas[row][column - 1] == self._horizontal_line:
            segments |= Junction.LEFT
        return self._junction_glyphs[segments]

    def _paint_cell(self, cell: tuple[int, int]) -> None:
        """Fill a cell interior using the terminal's current background."""
        self._terminal.move_cursor(self._layout.cell_interior(cell))
        self._terminal.write(self._cell_interior)

    def _draw_pattern(self) -> None:
        """Color fully closed pattern cells without touching their walls."""
        self._terminal.set_color(self.settings.pattern_color)
        for row, cells in enumerate(self._grid.cells):
            for column, value in enumerate(cells):
                if value == Wall.ALL:
                    self._paint_cell((row, column))
        self._terminal.reset_color()

    def _draw_path(self) -> None:
        """Paint the solution's interiors and the passages between them."""
        if not self.settings.show_path:
            return
        self._terminal.set_color(self.settings.path_color)
        cell = self._entry
        self._paint_cell(cell)
        for letter in self._solution:
            direction = self._directions_by_letter[letter]
            self._terminal.move_cursor(self._layout.passage(cell, direction))
            passage_fill = self._cell_interior if direction.row_offset else " "
            self._terminal.write(passage_fill)
            cell = direction.neighbor(cell)
            self._paint_cell(cell)
        self._terminal.reset_color()

    def _draw_endpoints(self) -> None:
        """Keep entry and exit markers visible above all other overlays."""
        for cell, marker, background in (
            (self._entry, "E", BackgroundColor.MAGENTA),
            (self._exit, "X", BackgroundColor.RED),
        ):
            self._terminal.move_cursor(self._layout.cell_interior(cell))
            self._terminal.set_color(background, ForegroundColor.BRIGHT_WHITE)
            self._terminal.write(
                marker.ljust(self._layout.cell_interior_width),
            )
        self._terminal.reset_color()

    def render(self) -> None:
        """Redraw walls and overlays, then position the cursor for the menu."""
        self._terminal.require_size(
            self._layout.required_columns, self._layout.required_rows,
        )
        try:
            self._terminal.clear()
            self._terminal.set_color(self.settings.wall_color)
            canvas = self._build_wall_canvas()
            self._terminal.write("\n".join("".join(row) for row in canvas))
            self._terminal.reset_color()
            self._draw_pattern()
            self._draw_path()
            self._draw_endpoints()
            self._terminal.move_cursor(self._layout.menu_position)
        finally:
            self._terminal.reset_color()
