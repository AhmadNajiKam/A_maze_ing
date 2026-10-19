#!/usr/bin/env python3
"""Generate, export and interactively display the configured maze."""

import sys

from mazegen import Config, DisplaySettings, MazeGenerator, Parser, Renderer
from mazegen.colors import parse_color
from mazegen.exporter import export_maze
from mazegen.menu import main_menu, regeneration_menu
from mazegen.solver import BFS


def generate_and_export(config: Config) -> tuple[list[list[int]], str]:
    """Coordinate generation, shortest-path solving, and file export."""
    maze = MazeGenerator(config).generate()
    solution = BFS(maze, config.entry_cell, config.exit_cell).solve()
    export_maze(config, maze, solution)
    return maze, solution


def choose_color(renderer: Renderer, choice: str) -> None:
    """Prompt for a named or custom color; blank input keeps the settings."""
    target, field = {
        "3": ("wall", "wall_color"),
        "4": ("path", "path_color"),
        "5": ("42 pattern", "pattern_color"),
    }[choice]
    print("Colors: red, green, yellow, blue,")
    print("magenta, cyan, white" + (", bright_white" if choice == "3" else ""))
    print("Or enter #RRGGBB (e.g. #FF8800).")
    while True:
        value = input(f"{target} color (blank cancels): ").strip()
        if not value:
            return
        try:
            color = parse_color(value, background=choice != "3")
        except ValueError as error:
            print(error)
            continue
        setattr(renderer.settings, field, color)
        return


def choose_seed(current_seed: int) -> int:
    """Choose a new seed or reuse/override the active seed in memory."""
    options, prompt = regeneration_menu()
    print("\n".join(options))
    while True:
        choice = input(prompt).strip()
        if choice == "1":
            return current_seed + 1
        if choice == "2":
            break
        print("Please enter a number from 1 to 2.")
    while True:
        value = input(
            f"Seed [{current_seed}] (Enter to keep current): "
        ).strip()
        if not value:
            return current_seed
        if value.isdecimal():
            try:
                return int(value)
            except ValueError:
                pass
        print("Seed must be a nonnegative decimal integer.")


def run_menu(config: Config, renderer: Renderer) -> None:
    """Handle user commands while preserving renderer preferences."""
    options, prompt = main_menu()
    while True:
        print("\n".join(options))
        choice = input(prompt).strip()
        if choice == "6":
            return
        try:
            if choice == "1":
                config.seed = choose_seed(config.seed)
                maze, solution = generate_and_export(config)
                renderer.replace_maze(
                    maze, solution, entry=config.entry_cell,
                    exit=config.exit_cell,
                )
            elif choice == "2":
                renderer.toggle_path()
            elif choice in {"3", "4", "5"}:
                choose_color(renderer, choice)
            else:
                print("Please enter a number from 1 to 6.")
                continue
            renderer.render()
        except (OSError, ValueError, MemoryError, OverflowError) as error:
            report_error(error)


def report_error(error: Exception) -> None:
    """Keep startup and menu error messages consistent."""
    if isinstance(error, OverflowError):
        print("Error: WIDTH or HEIGHT is too large for this system.")
    else:
        print(f"Error: {error}")


def main() -> None:
    """Read the configuration argument and launch the application."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return
    try:
        config = Parser().parse(sys.argv[1])
        maze, solution = generate_and_export(config)
        renderer = Renderer(
            maze, solution, entry=config.entry_cell, exit=config.exit_cell,
            settings=DisplaySettings(show_path=True),
        )
        renderer.render()
        run_menu(config, renderer)
    except (EOFError, KeyboardInterrupt):
        print("\nExiting.")
    except (OSError, ValueError, MemoryError, OverflowError) as error:
        report_error(error)


if __name__ == "__main__":
    main()
