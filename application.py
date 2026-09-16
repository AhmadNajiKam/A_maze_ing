#!/bin/usr/env python3
from maze_generator import MazeGenerator
from renderer import Renderer
from parser import Parser, Config


def main() -> None:
    parser = Parser()
    config: Config | None = parser._read_config("config.txt")

    if config is not None:
        mazeGen = MazeGenerator(config)
    maze: list[list[int]] = mazeGen._generate()
    mazeGen._put_42()
    rend = Renderer(maze)
    try:
        rend.render()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
