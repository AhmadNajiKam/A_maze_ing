"""One definition of maze coordinates, wall bits, and movement directions."""

from dataclasses import dataclass
from enum import IntFlag

Cell = tuple[int, int]  # Internal coordinates: (row, column).
Position = tuple[int, int]  # Configuration/export coordinates: (x, y).


class Wall(IntFlag):
    """A set bit represents a closed wall in the exported hexadecimal data."""

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8
    ALL = NORTH | EAST | SOUTH | WEST


@dataclass(frozen=True)
class Direction:
    """Relate a route letter, a cell offset, and both sides of a wall."""

    letter: str
    row_offset: int
    column_offset: int
    wall: Wall
    opposite_wall: Wall

    def neighbor(self, cell: Cell) -> Cell:
        """Return the adjacent cell in this direction."""
        row, column = cell
        return row + self.row_offset, column + self.column_offset


NORTH = Direction("N", -1, 0, Wall.NORTH, Wall.SOUTH)
EAST = Direction("E", 0, 1, Wall.EAST, Wall.WEST)
SOUTH = Direction("S", 1, 0, Wall.SOUTH, Wall.NORTH)
WEST = Direction("W", 0, -1, Wall.WEST, Wall.EAST)
DIRECTIONS = (NORTH, EAST, SOUTH, WEST)
DIRECTIONS_BY_LETTER = {
    direction.letter: direction for direction in DIRECTIONS
}
