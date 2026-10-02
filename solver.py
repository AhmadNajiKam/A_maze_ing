from collections import deque


class BFS:
    def __init__(
            self,
            maze: list[list[int]],
            entry: tuple[int, int],
            exit: tuple[int, int],):

        self.maze = maze
        self.entry = entry
        self.exit = exit

    def solve(self) -> str:
        queue = deque([self.entry])
        visited = {self.entry}
        parent: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

        while queue:
            current = queue.popleft()
            if current == self.exit:
                break
            for cell, direction in self._neighbors(current):
                if cell not in visited:
                    visited.add(cell)
                    parent[cell] = current, direction
                    queue.append(cell)

        if self.exit not in visited:
            raise ValueError("No path found from entry to exit")

        path = []
        current = self.exit

        while current != self.entry:
            current, direction = parent[current]
            path.append(direction)

        path.reverse()

        return ''.join(path)

    def _neighbors(self, cell: tuple[int, int]) -> list[tuple[tuple[int, int], str]]:
        row, col = cell
        value = self.maze[row][col]

        height = len(self.maze)
        width = len(self.maze[0])

        neighbors = []

        if row > 0 and not value & 1:
            neighbors.append(((row - 1, col), 'N'))

        if col < width - 1 and not value & 2:
            neighbors.append(((row, col + 1), 'E'))

        if row < height - 1 and not value & 4:
            neighbors.append(((row + 1, col), 'S'))

        if col > 0 and not value & 8:
            neighbors.append(((row, col - 1), 'W'))

        return neighbors
