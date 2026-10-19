"""Coordinate Sidewinder, connectivity repair, and constrained braiding."""

import random

from .config import Config
from .directions import Wall, make_directions
from .disjoint_set import DisjointSet
from .generation_rules import GenerationRules
from .grid import MazeGrid
from .pattern import PatternPlacer


class MazeGenerator:
    """Generate a connected grid using (row, column) coordinates."""

    def __init__(self, config: Config) -> None:
        """Store settings and a local random source for reproducible mazes."""
        self._config = config
        self._random = random.Random(config.seed)
        self._rules = GenerationRules()
        self._directions = make_directions()
        self._north, self._east, self._south, _ = self._directions

    def generate(self) -> list[list[int]]:
        """Return wall-bit rows, or raise if constraints cannot be met."""
        self._config.validate()
        self._random.seed(self._config.seed)
        self._blocked_cells = PatternPlacer(self._config, self._rules).place()
        for _ in range(self._rules.max_generation_attempts):
            self._reset_layout()
            self._carve_sidewinder_runs()
            self._connect_components()
            if self._config.perfect:
                return self._grid.cells
            self._braid_dead_ends()
            self._ensure_minimum_cycles()
            if self._meets_braiding_rules():
                return self._grid.cells
        raise ValueError(
            f"Could not build a board with "
            f"{self._rules.min_independent_cycles} loops "
            f"and at most {self._rules.max_dead_ends} dead ends after "
            f"{self._rules.max_generation_attempts} attempts. "
            "Try another seed or a larger size."
        )

    def _reset_layout(self) -> None:
        """Close walls and reset connectivity, retaining the chosen pattern."""
        self._grid = MazeGrid.closed(self._config.width, self._config.height)
        # Preserve row-major iteration so a seed has stable random choices.
        self._ordinary_cells: dict[tuple[int, int], None] = {
            (row, column): None
            for row in range(self._grid.height)
            for column in range(self._grid.width)
            if (row, column) not in self._blocked_cells
        }
        self._components = DisjointSet(self._ordinary_cells)
        self._neighbor_pairs: list[
            tuple[tuple[int, int], tuple[int, int]]
        ] = [
            (cell, neighbor) for cell in self._ordinary_cells
            for neighbor in (self._east.neighbor(cell),
                             self._south.neighbor(cell))
            if neighbor in self._ordinary_cells
        ]
        self._cycle_count = 0

    def _join_components(
        self, first: tuple[int, int], second: tuple[int, int],
    ) -> None:
        """Carve a passage only when it joins separate components."""
        if self._components.union(first, second):
            self._grid.open_passage(first, second)

    def _carve_sidewinder_runs(self) -> None:
        """Build eastward runs and select one northward passage per run."""
        for row in range(self._grid.height):
            north_candidates: list[tuple[int, int]] = []
            for column in range(self._grid.width):
                cell = (row, column)
                if cell not in self._ordinary_cells:
                    continue
                if self._north.neighbor(cell) in self._ordinary_cells:
                    north_candidates.append(cell)
                east_neighbor = self._east.neighbor(cell)
                east_blocked = east_neighbor not in self._ordinary_cells
                close_run = east_blocked or (
                    bool(north_candidates)
                    and self._random.choice((True, False))
                )
                if close_run:
                    self._finish_run(north_candidates)
                else:
                    self._join_components(cell, east_neighbor)

    def _finish_run(self, north_candidates: list[tuple[int, int]]) -> None:
        """Try one northward connection, then start a new horizontal run."""
        if north_candidates:
            cell = self._random.choice(north_candidates)
            self._join_components(cell, self._north.neighbor(cell))
        north_candidates.clear()

    def _connect_components(self) -> None:
        """Complete a spanning tree around the blocked pattern cells."""
        self._random.shuffle(self._neighbor_pairs)
        for first, second in self._neighbor_pairs:
            self._join_components(first, second)
        if self._components.component_count != 1:
            raise ValueError("The blocked pattern disconnects the maze")
        if not self._config.perfect:
            # A connected graph has E - V + 1 independent cycles available.
            possible_cycles = (
                len(self._neighbor_pairs) - len(self._ordinary_cells) + 1
            )
            if possible_cycles < self._rules.min_independent_cycles:
                raise ValueError(
                    "This grid is too small or narrow for two loops",
                )

    def _closed_neighbors(
        self, cell: tuple[int, int],
    ) -> list[tuple[int, int]]:
        """List ordinary neighbors that still have a separating wall."""
        return [direction.neighbor(cell) for direction in self._directions
                if direction.neighbor(cell) in self._ordinary_cells
                and self._grid.has_wall(cell, direction.wall)]

    def _area_is_fully_open(self, top_row: int, left_column: int) -> bool:
        """Check every internal eastward and southward wall of a square."""
        size = self._rules.forbidden_open_area_size
        horizontal_open = all(
            not self._grid.has_wall((row, column), Wall.EAST)
            for row in range(top_row, top_row + size)
            for column in range(left_column, left_column + size - 1)
        )
        vertical_open = all(
            not self._grid.has_wall((row, column), Wall.SOUTH)
            for row in range(top_row, top_row + size - 1)
            for column in range(left_column, left_column + size)
        )
        return horizontal_open and vertical_open

    def _creates_open_area(
        self, first: tuple[int, int], second: tuple[int, int],
    ) -> bool:
        """Inspect only squares containing the newly opened shared wall."""
        size = self._rules.forbidden_open_area_size
        first_row = max(0, max(first[0], second[0]) - (size - 1))
        last_row = min(min(first[0], second[0]), self._grid.height - size)
        first_column = max(0, max(first[1], second[1]) - (size - 1))
        last_column = min(min(first[1], second[1]), self._grid.width - size)
        return any(self._area_is_fully_open(row, column)
                   for row in range(first_row, last_row + 1)
                   for column in range(first_column, last_column + 1))

    def _try_adding_cycle(
        self, first: tuple[int, int], second: tuple[int, int],
    ) -> bool:
        """Open a wall unless doing so would create a forbidden open area."""
        direction = self._grid.direction_between(first, second)
        if not self._grid.has_wall(first, direction.wall):
            return False
        first_walls = self._grid.wall_value(first)
        second_walls = self._grid.wall_value(second)
        self._grid.open_passage(first, second)
        if self._creates_open_area(first, second):
            self._grid.set_wall_value(first, first_walls)
            self._grid.set_wall_value(second, second_walls)
            return False
        self._cycle_count += 1
        return True

    def _braid_dead_ends(self) -> None:
        """Prefer openings that remove two dead ends with one passage."""
        dead_ends = [cell for cell in self._ordinary_cells
                     if self._grid.is_dead_end(cell)]
        self._random.shuffle(dead_ends)
        for cell in dead_ends:
            if not self._grid.is_dead_end(cell):
                continue
            candidates = self._closed_neighbors(cell)
            self._random.shuffle(candidates)
            candidates.sort(
                key=lambda other: not self._grid.is_dead_end(other),
            )
            for neighbor in candidates:
                if self._try_adding_cycle(cell, neighbor):
                    break

    def _ensure_minimum_cycles(self) -> None:
        """Add any remaining required cycles where legal openings exist."""
        for first, second in self._neighbor_pairs:
            if self._cycle_count >= self._rules.min_independent_cycles:
                return
            self._try_adding_cycle(first, second)

    def _meets_braiding_rules(self) -> bool:
        """Check independent cycle and dead-end counts for this layout."""
        dead_end_count = sum(self._grid.is_dead_end(cell)
                             for cell in self._ordinary_cells)
        return (self._cycle_count >= self._rules.min_independent_cycles
                and dead_end_count <= self._rules.max_dead_ends)
