"""Union-Find connectivity tracking independent of maze wall storage."""

from collections.abc import Iterable


class DisjointSet:
    """Track components with path compression and union by size."""

    def __init__(self, cells: Iterable[tuple[int, int]]) -> None:
        """Start with one separate component for each cell."""
        self._parents = {cell: cell for cell in cells}
        self._sizes = {cell: 1 for cell in self._parents}
        self.component_count = len(self._parents)

    def find(self, cell: tuple[int, int]) -> tuple[int, int]:
        """Return the representative of a cell's connected component."""
        if self._parents[cell] != cell:
            self._parents[cell] = self.find(self._parents[cell])
        return self._parents[cell]

    def union(self, first: tuple[int, int], second: tuple[int, int]) -> bool:
        """Join separate components; report whether a merge occurred."""
        first_root, second_root = self.find(first), self.find(second)
        if first_root == second_root:
            return False
        if self._sizes[first_root] < self._sizes[second_root]:
            first_root, second_root = second_root, first_root
        self._parents[second_root] = first_root
        self._sizes[first_root] += self._sizes[second_root]
        self.component_count -= 1
        return True
