"""Draw Unicode maze walls using terminal cursor positioning."""

from enum import Enum
from os import system, get_terminal_size, read
import random
import select
import termios
import sys
import time
import tty


class Directions(int, Enum):
    """Represent closed walls at the four cardinal directions."""

    NORTH = 0b0001
    """East"""
    EAST = 0b0010
    """South"""
    SOUTH = 0b0100
    """West"""
    WEST = 0b1000


class Printable(str, Enum):
    """Retain the original Unicode wall and junction characters."""

    VLINE = "\u2503"
    """Upper Vertical Line ╹"""
    UVLINE = "\u2579"
    """Bottom Vertical Line ╻"""
    BVLINE = "\u257B"
    """Left Horizontal Line╸"""
    LHLINE = "\u2578"
    """Right Horizontal Line╺"""
    RHLINE = "\u257A"
    """Horizontal Line ━"""
    HLINE = "\u2501"
    """Upper-Left corner ┏"""
    ULCORNER = "\u250F"
    """Upper-Right corner ┓"""
    URCORNER = "\u2513"
    """Bottom-Left corner ┗"""
    BLCORNER = "\u2517"
    """Bottom-Right corner ┛"""
    BRCORNER = "\u251B"
    """Bottom-Half cross ┳"""
    BHCROSS = "\u2533"
    """Upper-Half cross ┻"""
    UHCROSS = "\u253B"
    """Left-Half cross ┫"""
    LHCROSS = "\u252B"
    """Right-Half cross ┣"""
    RHCROSS = "\u2523"
    """Cross ╋"""
    CROSS = "\u254B"

    def __str__(self) -> str:
        """Print the original glyph rather than its enum member name."""
        return str(self.value)


class Renderer:
    """Draw the original walls, with endpoint and optional path overlays."""

    _corner: dict[int, str] = {
        0: " ", 1: Printable.UVLINE, 2: Printable.RHLINE,
        3: Printable.BLCORNER, 4: Printable.BVLINE,  5: Printable.VLINE,
        6: Printable.ULCORNER, 7: Printable.RHCROSS, 8: Printable.LHLINE,
        9: Printable.BRCORNER, 10: Printable.HLINE, 11: Printable.UHCROSS,
        12: Printable.URCORNER, 13: Printable.LHCROSS, 14: Printable.BHCROSS,
        15: Printable.CROSS
    }

    def __init__(
        self, maze: list[list[int]], solution: str = "",
        show_path: bool = False, entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] | None = None, wall_color: int = 37,
        path_color: int = 46, pattern_color: int = 47,
    ) -> None:
        """Store maze, N/E/S/W solution, (x,y) endpoints and display state."""
        self._maze: list[list[int]] = maze
        self._solution = solution
        self._show_path = show_path
        self._entry = entry
        self._exit = exit if exit is not None else (
            len(maze[0]) - 1, len(maze) - 1,
        )
        self._wall_color = wall_color
        self._path_color = path_color
        self._pattern_color = pattern_color

    def toggle_path(self) -> None:
        """Toggle visibility without changing the maze or its solution."""
        self._show_path = not self._show_path

    def randomize_color(self) -> None:
        """Choose a different ANSI wall color without changing geometry."""
        self._wall_color = random.choice(
            [color for color in range(31, 38) if color != self._wall_color]
        )

    def rotate_path_color(self) -> None:
        """Rotate the solution background without changing the path."""
        self._path_color = 41 + (self._path_color - 40) % 7

    def rotate_pattern_color(self) -> None:
        """Rotate closed-cell interior color without changing walls."""
        self._pattern_color = 41 + (self._pattern_color - 40) % 7

    def _check_terminal_size(self) -> None:
        """Require a terminal large enough for the original maze and menu."""
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            raise ValueError("An interactive terminal is required for display")
        terminal = get_terminal_size(sys.stdout.fileno())

        required_cols = max(
            len(self._maze[0]) * 3 + 1,
            len("4. Change solution path color"),
            len("Choice (1-6): "),
        ) + 1
        required_rows = len(self._maze) * 2 + 11

        if (terminal.columns < required_cols
                or terminal.lines < required_rows):
            raise ValueError(
                f"Maze requires {required_cols} columns × "
                f"{required_rows} rows, "
                f"but the terminal has "
                f"{terminal.columns} columns × {terminal.lines} rows. "
                "Zoom out or enlarge the terminal."
            )

    def _cursor_position(self) -> tuple[int, int]:
        """Query cursor coordinates with a timeout and restore input mode."""
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            print(end="\x1b[6n", flush=True)

            response = ""
            deadline = time.monotonic() + 2
            while not response.endswith("R"):
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not select.select(
                    [fd], [], [], max(0, remaining)
                )[0]:
                    raise ValueError("Terminal did not report cursor position")
                char = read(fd, 1)
                if not char or len(response) >= 32:
                    raise ValueError("Invalid terminal cursor response")
                response += char.decode("ascii")

            if not response.startswith("\x1b["):
                raise ValueError("Invalid terminal cursor response")
            row, col = response[2:-1].split(";")
            if int(row) < 1 or int(col) < 1:
                raise ValueError("Invalid terminal cursor coordinates")
            return int(row), int(col)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def _render_borders(self) -> list[tuple[int, int]]:
        """Draw the original outer border and return drawing coordinates."""
        start_coordinates: tuple[int, int] = self._cursor_position()
        rows: int = len(self._maze) * 2
        cols: int = len(self._maze[0]) * 3
        for r in range(rows + 1):
            if r == 0:
                print(end=Printable.ULCORNER)
                for c in range(cols - 1):
                    print(end=Printable.HLINE)
                print(Printable.URCORNER)

            elif r == int(rows):
                print(end=Printable.BLCORNER)
                for c in range(cols - 1):
                    print(end=Printable.HLINE)
                print(Printable.BRCORNER)

            else:
                print(end=Printable.VLINE)
                for c in range(cols - 1):
                    print(end=" ")
                print(Printable.VLINE)
        end_coordinates: tuple[int, int] = self._cursor_position()
        return [(start_coordinates[0] + 1, start_coordinates[1]),
                end_coordinates]

    def _decide_corner(self, row: int, col: int) -> str:
        """Select the original junction glyph from neighboring wall bits."""
        hex_value: int = self._maze[row][col]
        hex_value_diagonal: int = self._maze[row + 1][col + 1]
        total: int = 0
        if hex_value & Directions.EAST:
            total += 1
        if hex_value & Directions.SOUTH:
            total += 8
        if hex_value_diagonal & Directions.NORTH:
            total += 2
        if hex_value_diagonal & Directions.WEST:
            total += 4
        return self._corner[total]

    def _draw(self, start_coordinates: tuple[int, int]) -> None:
        """Draw internal walls with the original three-by-two cell geometry."""
        col_length = len(self._maze[0])
        row_length = len(self._maze)
        for row in range(row_length):
            for col in range(col_length):
                if (col == col_length - 1
                        and row == row_length - 1):
                    continue
                place: tuple[int, int] = (
                    start_coordinates[0] + 1 + row * 2,
                    start_coordinates[1] + 1 + (col * 3))
                self._move_cursor(place)
                if self._maze[row][col] & Directions.SOUTH:
                    if row != row_length - 1:
                        if col == 0:
                            self._move_cursor((place[0], place[1] - 1))
                            print(end=Printable.RHCROSS)
                            print(end=2 * Printable.HLINE)
                        elif col == col_length - 1:
                            print(end=2 * Printable.HLINE)
                            print(end=Printable.LHCROSS)
                        else:
                            print(end=2 * Printable.HLINE)
                else:
                    print(end="  ")

                if row != row_length - 1 and col != col_length - 1:
                    print(end=self._decide_corner(row, col))
                self._move_cursor((place[0] - 1, place[1] + 2))

                if self._maze[row][col] & Directions.EAST:
                    print(end=Printable.VLINE)
                    if col != col_length - 1:
                        if row == 0:
                            self._move_cursor((place[0] - 2, place[1] + 2))
                            print(end=Printable.BHCROSS)
                        elif row == row_length - 1:
                            self._move_cursor((place[0], place[1] + 2))
                            print(end=Printable.UHCROSS)
                else:
                    print(end=" ")

    def _move_cursor(self, coordinates: tuple[int, int]) -> None:
        """Move to the absolute terminal (row, column) coordinates."""
        print(end=f"\x1B[{coordinates[0]};{coordinates[1]}H")

    def _draw_pattern(self, start_coordinates: tuple[int, int]) -> None:
        """Fill only the interiors of fully closed 42 cells with color."""
        print(end=f"\x1b[{self._pattern_color}m")
        for row, cells in enumerate(self._maze):
            for col, value in enumerate(cells):
                if value == 15:
                    self._move_cursor((start_coordinates[0] + row * 2,
                                       start_coordinates[1] + 1 + col * 3))
                    print(end="  ")
        print(end="\x1b[0m")

    def _draw_overlays(self, start_coordinates: tuple[int, int]) -> None:
        """Color interiors and open passages, leaving every wall untouched."""
        self._draw_pattern(start_coordinates)
        row = start_coordinates[0] + self._entry[1] * 2
        col = start_coordinates[1] + 1 + self._entry[0] * 3
        if self._show_path:
            print(end=f"\x1b[{self._path_color}m")
            self._move_cursor((row, col))
            print(end="  ")
            steps = {"N": (-2, 0), "E": (0, 3),
                     "S": (2, 0), "W": (0, -3)}
            for direction in self._solution:
                dr, dc = steps[direction]
                # Paint the open shared passage between the two interiors.
                passage = (row + dr // 2, col) if dr else (
                    row, col + 2 if dc > 0 else col - 1,
                )
                self._move_cursor(passage)
                print(end="  " if dr else " ")
                row, col = row + dr, col + dc
                self._move_cursor((row, col))
                print(end="  ")
            print(end="\x1b[0m")
        for (x, y), marker, color in (
            (self._entry, "E", 45), (self._exit, "X", 41),
        ):
            self._move_cursor((start_coordinates[0] + y * 2,
                               start_coordinates[1] + 1 + x * 3))
            print(end=f"\x1b[{color};97m{marker} \x1b[0m")

    def render(self) -> None:
        """Redraw the original Unicode maze, then its required overlays."""
        self._check_terminal_size()

        try:
            if system("clear") != 0:
                raise OSError("Could not clear the terminal; check TERM")
            print(end=f"\x1b[{self._wall_color}m")
            coordinates = self._render_borders()
            self._draw(coordinates[0])
            print(end="\x1b[0m")
            self._draw_overlays(coordinates[0])
            self._move_cursor(coordinates[1])
        except termios.error as error:
            raise OSError(f"Terminal error: {error}") from error
        finally:
            print(end="\x1b[0m", flush=True)
