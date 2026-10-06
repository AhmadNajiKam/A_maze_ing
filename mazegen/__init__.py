"""Reuse the maze generator, configuration and original BFS solver.

Basic example (coordinates in Config are x,y; BFS uses row,column)::

    from mazegen import Config, MazeGenerator, solver

    config = Config([20, 15, (0, 0), (19, 14), "maze.txt", True, 3])
    maze = MazeGenerator(config)._generate()
    solution = solver.BFS(maze, (0, 0), (14, 19)).solve()

The Config list is [width, height, entry, exit, output_file, perfect, seed].
Change size, endpoints and seed there to supply custom parameters. The return
value of _generate() is a row-major list of wall-bit integers: N=1, E=2, S=4,
W=8; set bits are closed walls. solve() returns shortest N/E/S/W directions.
Generation itself does not write files or launch the terminal application.
Invalid or impossible parameters and unreachable solutions raise ValueError.
See the included MIT license for reuse and distribution terms.
"""

from .maze_generator import MazeGenerator
from .parser import Config, Parser
from .renderer import Renderer
from . import solver

__all__ = ["MazeGenerator", "Config", "Parser", "Renderer", "solver"]
