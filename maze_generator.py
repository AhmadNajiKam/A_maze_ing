"""Generate connected perfect or braided mazes using four wall bits."""

import random

from parser import Config


class MazeGenerator:
    """Keep a Sidewinder tree, then optionally add constrained loops.

    Config entry/exit coordinates use (x, y). Generated arrays use [y][x].
    _generate() raises ValueError for invalid or unsuccessful parameters;
    the application's error handler should display that message.
    """

    def __init__(self, config: Config) -> None:
        """Store configuration and initialise generation state."""
        # Row offset, column offset, current wall, opposite wall.
        self._directions = (
            (-1, 0, 1, 4), (0, 1, 2, 8),
            (1, 0, 4, 1), (0, -1, 8, 2),
        )
        self._config = config
        self._height = config._HEIGHT
        self._width = config._WIDTH
        self._rng = random.Random(config._SEED)
        self._maze: list[list[int]] = []
        self._blocked: set[tuple[int, int]] = set()
        self._parent: dict[tuple[int, int], tuple[int, int]] = {}
        self._size: dict[tuple[int, int], int] = {}
        self._edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
        self._cycles = 0

    def _generate(self) -> list[list[int]]:
        """Try at most 30 layouts and return a board meeting the checks."""
        self._check_config()
        self._rng.seed(self._config._SEED)
        self._put_42()
        for _ in range(30):
            self._reset()
            self._sidewinder()
            self._connect()
            if self._config._PERFECT:
                return self._maze
            self._braid()
            self._add_loops()
            if self._playable():
                return self._maze
        raise ValueError(
            "Could not build a board with two loops and at most two "
            "dead ends after 30 attempts. Try another seed or a larger size."
        )

    def _check_config(self) -> None:
        """Reject invalid dimensions, endpoints and out-of-bounds cells."""
        if self._height < 1 or self._width < 1:
            raise ValueError("WIDTH and HEIGHT must be positive")
        if self._config._ENTRY == self._config._EXIT:
            raise ValueError("ENTRY and EXIT must be different")
        for x, y in (self._config._ENTRY, self._config._EXIT):
            if not (0 <= x < self._width and 0 <= y < self._height):
                raise ValueError("ENTRY and EXIT must be inside the maze")

    def _put_42(self) -> None:
        """Place 42 near the centre without blocking reserved cells."""
        pattern = (
            "1000111", "1000001", "1110111", "0010100", "0010111",
        )
        self._blocked.clear()
        if self._height < 7 or self._width < 9:
            print("Warning: maze too small for the 42 pattern; omitted.")
            return
        entry_x, entry_y = self._config._ENTRY
        exit_x, exit_y = self._config._EXIT
        reserved = {(entry_y, entry_x), (exit_y, exit_x)}
        if not self._config._PERFECT:
            reserved.add((self._height // 2, self._width // 2))
        centre_r = (self._height - 5) // 2
        centre_c = (self._width - 7) // 2
        positions = [(r, c) for r in range(1, self._height - 5)
                     for c in range(1, self._width - 7)]
        positions.sort(key=lambda p: abs(p[0] - centre_r)
                       + abs(p[1] - centre_c))
        for row, col in positions:
            blocked = {(row + r, col + c)
                       for r, line in enumerate(pattern)
                       for c, value in enumerate(line) if value == "1"}
            if not (blocked & reserved):
                self._blocked = blocked
                return
        raise ValueError("Cannot place 42 clear of the centre, ENTRY and EXIT")

    def _reset(self) -> None:
        """Reset walls and Union-Find, retaining the chosen pattern."""
        self._maze = [[15] * self._width for _ in range(self._height)]
        self._parent = {(r, c): (r, c)
                        for r in range(self._height)
                        for c in range(self._width)
                        if (r, c) not in self._blocked}
        self._size = {cell: 1 for cell in self._parent}
        self._edges = [(a, b) for a in self._parent
                       for b in ((a[0], a[1] + 1), (a[0] + 1, a[1]))
                       if b in self._parent]
        self._cycles = 0

    def _root(self, cell: tuple[int, int]) -> tuple[int, int]:
        """Find a component representative using path compression."""
        if self._parent[cell] != cell:
            self._parent[cell] = self._root(self._parent[cell])
        return self._parent[cell]

    def _wall_pair(
        self, a: tuple[int, int], b: tuple[int, int]
    ) -> tuple[int, int]:
        """Return the two wall bits separating adjacent cells."""
        offset = (b[0] - a[0], b[1] - a[1])
        for dr, dc, wall, opposite in self._directions:
            if offset == (dr, dc):
                return wall, opposite
        raise ValueError("Can only connect orthogonally adjacent cells")

    def _open_wall(self, a: tuple[int, int], b: tuple[int, int]) -> None:
        """Clear both sides of a shared wall between ordinary cells."""
        wall, opposite = self._wall_pair(a, b)
        self._maze[a[0]][a[1]] &= ~wall
        self._maze[b[0]][b[1]] &= ~opposite

    def _carve(self, a: tuple[int, int], b: tuple[int, int]) -> None:
        """Join distinct components without creating a cycle."""
        ra, rb = self._root(a), self._root(b)
        if ra == rb:
            return
        self._open_wall(a, b)
        if self._size[ra] < self._size[rb]:
            ra, rb = rb, ra
        self._parent[rb] = ra
        self._size[ra] += self._size[rb]

    def _sidewinder(self) -> None:
        """Create horizontal runs with one northward selection per run."""
        for r in range(self._height):
            north: list[tuple[int, int]] = []
            for c in range(self._width):
                if (r, c) not in self._parent:
                    north.clear()
                    continue
                if (r - 1, c) in self._parent:
                    north.append((r, c))
                east_blocked = (r, c + 1) not in self._parent
                close_run = east_blocked or (
                    bool(north) and self._rng.choice((True, False))
                )
                if close_run:
                    self._finish_run(north)
                else:
                    self._carve((r, c), (r, c + 1))

    def _finish_run(self, north: list[tuple[int, int]]) -> None:
        """Try one northward connection, then clear the run candidates."""
        if north:
            r, c = self._rng.choice(north)
            self._carve((r, c), (r - 1, c))
        north.clear()

    def _connect(self) -> None:
        """Complete the spanning tree using shuffled neighboring pairs."""
        self._rng.shuffle(self._edges)
        for a, b in self._edges:
            self._carve(a, b)
        if len({self._root(cell) for cell in self._parent}) != 1:
            raise ValueError("The blocked pattern disconnects the maze")
        possible_cycles = len(self._edges) - len(self._parent) + 1
        if not self._config._PERFECT and possible_cycles < 2:
            raise ValueError("This grid is too small or narrow for two loops")

    def _is_dead_end(self, cell: tuple[int, int]) -> bool:
        """Report whether exactly one of the four passages is open."""
        value = self._maze[cell[0]][cell[1]]
        return sum(not (value & wall)
                   for _, _, wall, _ in self._directions) == 1

    def _closed_neighbors(
        self, cell: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """List ordinary neighbors separated from cell by a closed wall."""
        r, c = cell
        return [(r + dr, c + dc) for dr, dc, wall, _ in self._directions
                if (r + dr, c + dc) in self._parent
                and self._maze[r][c] & wall]

    def _open_square(self, row: int, col: int) -> bool:
        """Check the twelve internal shared walls of one 3-by-3 block."""
        horizontal = all(not (self._maze[r][c] & 2)
                         for r in range(row, row + 3)
                         for c in range(col, col + 2))
        vertical = all(not (self._maze[r][c] & 4)
                       for r in range(row, row + 2)
                       for c in range(col, col + 3))
        return horizontal and vertical

    def _creates_open_square(
        self, a: tuple[int, int], b: tuple[int, int]
    ) -> bool:
        """Inspect only 3-by-3 blocks containing the changed shared wall."""
        first_r = max(0, max(a[0], b[0]) - 2)
        last_r = min(min(a[0], b[0]), self._height - 3)
        first_c = max(0, max(a[1], b[1]) - 2)
        last_c = min(min(a[1], b[1]), self._width - 3)
        return any(self._open_square(r, c)
                   for r in range(first_r, last_r + 1)
                   for c in range(first_c, last_c + 1))

    def _try_loop(self, a: tuple[int, int], b: tuple[int, int]) -> bool:
        """After connectivity repair, add a loop unless it opens a 3x3 area."""
        wall, _ = self._wall_pair(a, b)
        old_a = self._maze[a[0]][a[1]]
        old_b = self._maze[b[0]][b[1]]
        if not (old_a & wall):
            return False
        self._open_wall(a, b)
        if self._creates_open_square(a, b):
            self._maze[a[0]][a[1]] = old_a
            self._maze[b[0]][b[1]] = old_b
            return False
        self._cycles += 1
        return True

    def _braid(self) -> None:
        """Try to give every dead end a second exit without large rooms."""
        dead_ends = [cell for cell in self._parent
                     if self._is_dead_end(cell)]
        self._rng.shuffle(dead_ends)
        for cell in dead_ends:
            if not self._is_dead_end(cell):
                continue
            candidates = self._closed_neighbors(cell)
            self._rng.shuffle(candidates)
            candidates.sort(key=lambda other: not self._is_dead_end(other))
            for neighbor in candidates:
                if self._try_loop(cell, neighbor):
                    break

    def _add_loops(self) -> None:
        """Ensure at least two independent cycles, if legal openings exist."""
        for a, b in self._edges:
            if self._cycles >= 2:
                return
            self._try_loop(a, b)

    def _playable(self) -> bool:
        """Apply the subject's minimum loops and tolerated dead-end count."""
        dead_ends = sum(self._is_dead_end(cell) for cell in self._parent)
        return self._cycles >= 2 and dead_ends <= 2
