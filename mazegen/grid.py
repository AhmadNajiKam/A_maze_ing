"""Wall storage and operations that keep neighboring cells coherent."""

from .directions import Direction, Wall, make_directions


class MazeGrid:
    """Wrap a row-major wall array without copying it."""

    def __init__(self, cells: list[list[int]]) -> None:
        """Require a nonempty rectangular grid of wall-bit values."""
        if not cells or not cells[0]:
            raise ValueError("Maze must contain at least one cell")
        self.height = len(cells)
        self.width = len(cells[0])
        if any(len(row) != self.width for row in cells):
            raise ValueError("Maze rows must have equal widths")
        self.cells = cells
        self._directions = make_directions()

    @classmethod
    def closed(cls, width: int, height: int) -> "MazeGrid":
        """Create a grid with all four walls closed in every cell."""
        return cls([[int(Wall.ALL)] * width for _ in range(height)])

    def contains(self, cell: tuple[int, int]) -> bool:
        """Return whether a (row, column) coordinate lies within the grid."""
        row, column = cell
        return 0 <= row < self.height and 0 <= column < self.width

    def wall_value(self, cell: tuple[int, int]) -> int:
        """Read the four wall bits of a cell."""
        row, column = cell
        return self.cells[row][column]

    def set_wall_value(self, cell: tuple[int, int], value: int) -> None:
        """Restore a cell's wall bits, for example after a rejected opening."""
        row, column = cell
        self.cells[row][column] = int(value)

    def has_wall(self, cell: tuple[int, int], wall: Wall) -> bool:
        """Return whether the requested wall is closed."""
        return bool(self.wall_value(cell) & wall)

    def direction_between(
        self, first: tuple[int, int], second: tuple[int, int],
    ) -> Direction:
        """Find the direction joining two orthogonally adjacent cells."""
        for direction in self._directions:
            if direction.neighbor(first) == second:
                return direction
        raise ValueError("Can only connect orthogonally adjacent cells")

    def open_passage(
        self, first: tuple[int, int], second: tuple[int, int],
    ) -> None:
        """Clear both sides of a shared wall."""
        direction = self.direction_between(first, second)
        self.set_wall_value(first, self.wall_value(first) & ~direction.wall)
        self.set_wall_value(
            second, self.wall_value(second) & ~direction.opposite_wall,
        )

    def reachable_neighbors(
        self, cell: tuple[int, int],
    ) -> list[tuple[tuple[int, int], str]]:
        """List in-bounds neighbors accessible through open passages."""
        return [(direction.neighbor(cell), direction.letter)
                for direction in self._directions
                if self.contains(direction.neighbor(cell))
                and not self.has_wall(cell, direction.wall)]

    def is_dead_end(self, cell: tuple[int, int]) -> bool:
        """A dead end has exactly one reachable neighbor."""
        return len(self.reachable_neighbors(cell)) == 1
