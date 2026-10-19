"""Write the specified hexadecimal maze and shortest-path file format."""

from .config import Config


def export_maze(config: Config, maze: list[list[int]], solution: str) -> None:
    """Write wall rows, a blank line, x,y endpoints, and route directions."""
    with open(config.output_file, "w", encoding="utf-8", newline="\n") as file:
        for row in maze:
            file.write("".join(f"{walls:X}" for walls in row) + "\n")
        file.write("\n")
        for x, y in (config.entry, config.exit):
            file.write(f"{x},{y}\n")
        file.write(solution + "\n")
