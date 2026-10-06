#!/usr/bin/env python3
"""Generate, export and interactively display the configured maze."""

import sys

from mazegen import MazeGenerator, Parser, Config, solver, Renderer


def main() -> None:
    """Read the sole config argument and run the six-choice terminal menu."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return
    try:
        parser = Parser()
        config: Config | None = parser._read_config(sys.argv[1])
        if config is None:
            return
        maze, solution = generation(config)
        rend = Renderer(
            maze, solution, show_path=True,
            entry=config._ENTRY, exit=config._EXIT,
        )
        rend.render()
        while True:
            print(
                """1. Re-generate maze
2. Show/Hide shortest path
3. Change maze wall colors
4. Change solution path color
5. Change 42 pattern color
6. Exit"""
            )
            try:
                choice = int(input("Choice (1-6): "))
            except ValueError:
                print("Please enter a number from 1 to 6.")
                continue
            try:
                match choice:
                    case 1:
                        config._SEED += 1
                        maze, solution = generation(config)
                        rend = Renderer(
                            maze, solution, show_path=rend._show_path,
                            entry=config._ENTRY, exit=config._EXIT,
                            wall_color=rend._wall_color,
                            path_color=rend._path_color,
                            pattern_color=rend._pattern_color,
                        )
                        rend.render()
                    case 2:
                        rend.toggle_path()
                        rend.render()
                    case 3:
                        rend.randomize_color()
                        rend.render()
                    case 4:
                        rend.rotate_path_color()
                        rend.render()
                    case 5:
                        rend.rotate_pattern_color()
                        rend.render()
                    case 6:
                        break
                    case _:
                        print("Please enter a number from 1 to 6.")
            except OverflowError:
                print("Error: WIDTH or HEIGHT is too large for this system.")
            except (OSError, ValueError, MemoryError) as error:
                print(f"Error: {error}")
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")
    except OverflowError:
        print("Error: WIDTH or HEIGHT is too large for this system.")
    except (OSError, ValueError, MemoryError) as error:
        print(f"Error: {error}")


def generation(
    config: Config,
) -> tuple[list[list[int]], str]:
    """Generate, solve and write the exact subject format; return both values.

    Config endpoints use (x, y). BFS endpoints use (row, column).
    Generation, solving and file errors propagate to main() for reporting.
    """
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

    with open(
        config._OUTPUT_FILE, "w", encoding="utf-8", newline="\n"
    ) as file:
        for row in maze:
            file.write("".join(f"{cell:X}" for cell in row) + "\n")
        file.write("\n")
        file.write(f"{config._ENTRY[0]},{config._ENTRY[1]}\n")
        file.write(f"{config._EXIT[0]},{config._EXIT[1]}\n")
        file.write(solution + "\n")

    return maze, solution


if __name__ == "__main__":
    main()
