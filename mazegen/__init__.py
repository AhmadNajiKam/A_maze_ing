"""Generate and solve mazes without launching the terminal application.

    from mazegen import BFS, Config, MazeGenerator

    config = Config(
        width=20, height=15, entry=(0, 0), exit=(19, 14),
        output_file="maze.txt", perfect=True, seed=3,
    )
    maze = MazeGenerator(config).generate()
    solution = BFS(maze, config.entry_cell, config.exit_cell).solve()

Customize width, height, seed, and the other named Config fields before
instantiating MazeGenerator. generate() returns a list[list[int]] indexed as
maze[row][column]; BFS.solve() returns a shortest path string using N/E/S/W.

Config and export endpoints use (x, y); grid, solver, and renderer coordinates
use (row, column). Config.entry_cell and Config.exit_cell convert between them.
Wall bits are N=1, E=2, S=4, W=8; a set bit means closed. Invalid or impossible
settings and unreachable exits raise ValueError. Parser.parse() raises errors
with filename context. Generation itself performs no file or terminal I/O,
apart from warning when the 42 pattern cannot be placed.
"""

# Explicit re-exports keep the public API without a module-level __all__ list.
from .config import Config as Config  # noqa: F401
from .directions import Wall as Wall  # noqa: F401
from .grid import MazeGrid as MazeGrid  # noqa: F401
from .maze_generator import MazeGenerator as MazeGenerator  # noqa: F401
from .parser import Parser as Parser  # noqa: F401
from .renderer import DisplaySettings as DisplaySettings  # noqa: F401
from .renderer import Renderer as Renderer  # noqa: F401
from .solver import BFS as BFS  # noqa: F401
from . import solver as solver  # noqa: F401
