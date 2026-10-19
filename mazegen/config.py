"""Typed settings shared by configuration readers and maze clients."""

from dataclasses import dataclass


@dataclass(kw_only=True)
class Config:
    """Describe a maze; external endpoint coordinates are (x, y)."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int

    def validate(self) -> None:
        """Reject dimensions and endpoints that cannot describe a maze."""
        if self.height < 1 or self.width < 1:
            raise ValueError("WIDTH and HEIGHT must be positive")
        if self.entry == self.exit:
            raise ValueError("ENTRY and EXIT must be different")
        for x, y in (self.entry, self.exit):
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ValueError("ENTRY and EXIT must be inside the maze")

    @property
    def entry_cell(self) -> tuple[int, int]:
        """Convert the entry to the internal (row, column) convention."""
        x, y = self.entry
        return y, x

    @property
    def exit_cell(self) -> tuple[int, int]:
        """Convert the exit to the internal (row, column) convention."""
        x, y = self.exit
        return y, x
