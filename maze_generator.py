from parser import Config
import random


class MazeGenerator:
    def __init__(self, config: Config) -> None:
        self._config = config

        self._maze: list[list[int]] = []
        self._blocked: set[tuple[int, int]] = set()

    def _put_42(self) -> None:
        pattern = [
            "1000111",
            "1000001",
            "1110111",
            "0010100",
            "0010111",
        ]

        height = len(self._maze)
        width = len(self._maze[0])

        start_row = (height - len(pattern)) // 2
        start_col = (width - len(pattern[0])) // 2

        # These cells already have four walls. Reserve their coordinates
        # so the generator never opens them.
        self._blocked = {
            (start_row + r, start_col + c)
            for r, line in enumerate(pattern)
            for c, value in enumerate(line)
            if value == "1"
        }

    def _generate(self) -> list[list[int]]:
        height = self._config._HEIGHT
        width = self._config._WIDTH

        # Leave at least one cell around the pattern.
        if height < 7 or width < 9:
            raise ValueError("Maze must be at least 9 columns by 7 rows")

        rng = random.Random(self._config._SEED)
        self._maze = [[15] * width for _ in range(height)]
        self._put_42()

        # Start to track which ordinary cells are already connected.
        # This initilize a dictionary of parents that represent root nodes
        # Ex: A: A, B: B etc .. where A is a tuple of (row, col)
        parent = {
            (r, c): (r, c)
            for r in range(height)
            for c in range(width)
            if (r, c) not in self._blocked
        }

        # This tracks the size of each group represented by the roots we
        # defined in parent dictionary
        size = {cell: 1 for cell in parent}

        def root(cell: tuple[int, int]) -> tuple[int, int]:
            if parent[cell] != cell:
                parent[cell] = root(parent[cell])
            return parent[cell]

        def carve(a: tuple[int, int], b: tuple[int, int]) -> None:
            root_a, root_b = root(a), root(b)

            if root_a == root_b:
                return  # Opening another connection would create a loop.

            first_r, first_c = a
            second_r, second_c = b

            # Key is second cell offset relative to the first cell
            walls = {
                (-1, 0): (1, 4),
                (0, 1): (2, 8),
                (1, 0): (4, 1),
                (0, -1): (8, 2),
            }
            wall, opposite = walls[(second_r - first_r, second_c - first_c)]

            self._maze[first_r][first_c] &= ~wall
            self._maze[second_r][second_c] &= ~opposite

            # Merge the root_b region into root_a region.
            if size[root_a] < size[root_b]:
                root_a, root_b = root_b, root_a

            parent[root_b] = root_a
            size[root_a] += size[root_b]

        for r in range(height):
            north_candidates: list[tuple[int, int]] = []

            for c in range(width):
                if (r, c) in self._blocked:
                    north_candidates.clear()
                    continue

                # Only cells with an ordinary cell above can open north.
                if r > 0 and (r - 1, c) not in self._blocked:
                    north_candidates.append((r, c))

                east_blocked = (
                    c == width - 1
                    or (r, c + 1) in self._blocked
                )

                close_run = east_blocked or (
                    bool(north_candidates)
                    and rng.choice([True, False])
                )

                if close_run:
                    if north_candidates:
                        nr, nc = rng.choice(north_candidates)
                        carve((nr, nc), (nr - 1, nc))

                    north_candidates.clear()
                else:
                    carve((r, c), (r, c + 1))

        # 42 pattern cells can leave disconnected regions after Sidewinder.
        # Consider each ordinary neighboring pair once.
        edges = [
            ((r, c), (r + nr, c + nc))
            for r, c in parent
            for nr, nc in ((0, 1), (1, 0))
            if (r + nr, c + nc) in parent
        ]

        rng.shuffle(edges)

        for a, b in edges:
            carve(a, b)  # Opens a wall only between different regions.

        return self._maze
