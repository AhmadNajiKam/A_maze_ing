#!/usr/bin/env python3
from mazegen import MazeGenerator, Parser, Config, solver, Renderer


def main() -> None:
    try:
        parser = Parser()
        config: Config | None = parser._read_config("config.txt")
    except Exception as e:
        print(e)
        return

    if config is None:
        print("Config file is invalid")
        return

    maze, solution = generation(config)

    rend = Renderer(
        maze,
        solution,
        show_path=True,
    )

    try:
        rend.render()
    except Exception as e:
        print(e)

    print(
        """1. Re-generate a new maze and display it
2. Show/Hide shortest path
3. Change maze wall colors
4. Exit"""
    )

    while True:
        choice = int(input("Please enter a number: "))

        match choice:
            case 1:
                config._SEED += 1

                maze, solution = generation(config)

                rend = Renderer(
                    maze,
                    solution,
                )

                try:
                    rend.render()
                except Exception as e:
                    print(e)

            case 2:
                rend.toggle_path()

                try:
                    rend.render()
                except Exception as e:
                    print(e)

            case 3:
                rend.randomize_color()

                try:
                    rend.render()
                except Exception as e:
                    print(e)

            case 4:
                break


def generation(
    config: Config,
) -> tuple[list[list[int]], str]:
    maze_gen = MazeGenerator(config)

    maze: list[list[int]] = maze_gen._generate()

    entry_cell = (
        config._ENTRY[1],
        config._ENTRY[0],
    )

    exit_cell = (
        config._EXIT[1],
        config._EXIT[0],
    )

    algo = solver.BFS(
        maze,
        entry_cell,
        exit_cell,
    )

    solution = algo.solve()

    return maze, solution


if __name__ == "__main__":
    main()
