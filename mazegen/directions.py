"""One definition of maze coordinates, wall bits, and movement directions."""

from dataclasses import dataclass
from enum import IntFlag


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

    def neighbor(self, cell: tuple[int, int]) -> tuple[int, int]:
        """Return the adjacent cell in this direction."""
        row, column = cell
        return row + self.row_offset, column + self.column_offset


def make_directions() -> tuple[Direction, ...]:
    """Build fresh directions in stable north/east/south/west order."""
    return (
        Direction("N", -1, 0, Wall.NORTH, Wall.SOUTH),
        Direction("E", 0, 1, Wall.EAST, Wall.WEST),
        Direction("S", 1, 0, Wall.SOUTH, Wall.NORTH),
        Direction("W", 0, -1, Wall.WEST, Wall.EAST),
    )
