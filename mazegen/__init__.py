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

from .config import Config
from .directions import Wall
from .grid import MazeGrid
from .maze_generator import MazeGenerator
from .parser import Parser
from .renderer import DisplaySettings, Renderer
from .solver import BFS
from . import solver

__all__ = [
    "BFS", "Config", "DisplaySettings", "MazeGenerator", "MazeGrid", "Parser",
    "Renderer", "Wall", "solver",
]
