"""Choose a connected, endpoint-safe placement for the blocked 42 cells."""

from .config import Config
from .directions import Cell, DIRECTIONS
from .generation_rules import MAX_DEAD_ENDS

PATTERN_42 = (
    "1000111",
    "1000001",
    "1110111",
    "0010100",
    "0010111",
)


class PatternPlacer:
    """Prefer central interior placements without isolating ordinary cells."""

    def __init__(self, config: Config) -> None:
        """Store board dimensions and cells that the pattern must not cover."""
        self._config = config
        self._pattern_height = len(PATTERN_42)
        self._pattern_width = len(PATTERN_42[0])

    def place(self) -> set[Cell]:
        """Return blocked cells, or warn and omit an infeasible pattern."""
        reserved = self._reserved_cells()
        for origin in self._candidate_origins():
            blocked = self._blocked_cells(origin)
            if not blocked & reserved and self._placement_is_playable(blocked):
                return blocked
        print("Warning: no eligible placement for the 42 pattern; omitted.")
        return set()

    def _reserved_cells(self) -> set[Cell]:
        """Protect endpoints, plus corners and centre in non-perfect mode."""
        height, width = self._config.height, self._config.width
        reserved = {self._config.entry_cell, self._config.exit_cell}
        if not self._config.perfect:
            reserved.update({(height // 2, width // 2), (0, 0),
                             (0, width - 1), (height - 1, 0),
                             (height - 1, width - 1)})
        return reserved

    def _candidate_origins(self) -> list[Cell]:
        """Order origins by interior preference, then distance from centre."""
        last_row = self._config.height - self._pattern_height
        last_column = self._config.width - self._pattern_width
        centre_row, centre_column = last_row // 2, last_column // 2
        origins = [(row, column)
                   for row in range(last_row + 1)
                   for column in range(last_column + 1)]
        origins.sort(key=lambda origin: (
            origin[0] in (0, last_row) or origin[1] in (0, last_column),
            abs(origin[0] - centre_row) + abs(origin[1] - centre_column),
        ))
        return origins

    def _blocked_cells(self, origin: Cell) -> set[Cell]:
        """Translate the pattern bitmap to board coordinates."""
        origin_row, origin_column = origin
        return {(origin_row + row, origin_column + column)
                for row, line in enumerate(PATTERN_42)
                for column, value in enumerate(line) if value == "1"}

    def _placement_is_playable(self, blocked: set[Cell]) -> bool:
        """Check connectivity and forced dead ends before carving walls."""
        start = self._config.entry_cell
        seen = {start}
        pending = [start]
        forced_dead_ends = 0
        while pending:
            cell = pending.pop()
            neighbor_count = 0
            for direction in DIRECTIONS:
                neighbor = direction.neighbor(cell)
                row, column = neighbor
                if (0 <= row < self._config.height
                        and 0 <= column < self._config.width
                        and neighbor not in blocked):
                    neighbor_count += 1
                    if neighbor not in seen:
                        seen.add(neighbor)
                        pending.append(neighbor)
            forced_dead_ends += neighbor_count == 1
        ordinary_cell_count = (
            self._config.height * self._config.width - len(blocked)
        )
        return (len(seen) == ordinary_cell_count
                and (self._config.perfect
                     or forced_dead_ends <= MAX_DEAD_ENDS))
