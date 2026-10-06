*This activity has been created as part of the 42 curriculum by mhaddad, Akamamji.*

# A-Maze-ing

## Description

A-Maze-ing is a Python project that generates a maze from a configuration file,
finds a shortest path, exports hexadecimal wall data, and displays the result in
an interactive Unicode terminal. The goal is to practise algorithms, modular
programming, and building a reusable Python package.

The generator combines Sidewinder with Union-Find and optional braiding. Both
modes keep ordinary cells connected, shared walls coherent, external borders
closed, and avoid fully open 3×3 areas. Fully closed cells form a visible “42”
when an eligible placement exists; otherwise a warning explains its omission.

## Instructions

Use Python 3.10 or later, [uv](https://docs.astral.sh/uv/), Make, and a Unix-like
terminal supporting Unicode, ANSI colors, and cursor-position queries. There
are no third-party runtime dependencies. Run these commands from the project
root; Python source does not need a separate compilation step:

```sh
make install
. .venv/bin/activate
python3 a_maze_ing.py config.txt
```

`make install` runs `uv sync` to prepare the environment and development tools.
The program accepts exactly one argument: a configuration filename, which can
be different from `config.txt`. You can also run it with:

```sh
make run
# Or use a different configuration file:
# Replace config.txt below with that filename.
uv run python a_maze_ing.py config.txt
```

`make run` uses the supplied `config.txt`; `make debug` runs it through `pdb`.
The terminal must have at least `max(3 * WIDTH + 2, 30)` columns and
`2 * HEIGHT + 11` rows, including room for the menu. The supplied 40×20 grid
needs 122 columns and 51 rows. Enlarge the terminal or zoom out if needed.
A successful non-interactive run exports the maze, then reports that display
requires a terminal. Relative file paths use the current working directory.

### Configuration format

Use one `KEY=VALUE` pair per line, in any order. Blank lines and comment lines
starting with `#` (also after indentation) are ignored. Comments occupy their
own line. Keys are case-insensitive and surrounding key/value whitespace is
ignored. Duplicate or unknown keys, missing required keys, and invalid values
are reported as errors.

| Key | Required | Format |
| --- | --- | --- |
| `WIDTH` | Yes | Positive integer number of columns |
| `HEIGHT` | Yes | Positive integer number of rows |
| `ENTRY` | Yes | Nonnegative integers `x,y`, inside the grid |
| `EXIT` | Yes | Nonnegative integers `x,y`, inside the grid; different from entry |
| `OUTPUT_FILE` | Yes | Nonempty output filename/path |
| `PERFECT` | Yes | `True` or `False`, case-insensitive |
| `SEED` | No | Nonnegative integer; randomly chosen when omitted |

Write numbers as decimal digits without signs, and coordinates without spaces
around the comma. The supplied `config.txt` contains:

```text
WIDTH=40
HEIGHT=20
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=3
```

`PERFECT` must be provided explicitly; the supplied configuration selects
`True`. If `SEED` is omitted, the parser chooses a random 64-bit seed. An
explicit seed with the same other parameters reproduces the maze. Regeneration
increments the current seed.

### Menu and display

1. Re-generate maze
2. Show/Hide shortest path
3. Change maze wall colors
4. Change solution path color
5. Change 42 pattern color
6. Exit

Enter a number at `Choice (1-6): ` and press Enter. `E` marks the entry and `X`
the exit. The shortest path is initially shown in cyan; the 42 interiors are
initially white. Option 3 randomly selects a different wall color; options 4
and 5 cycle the path and pattern colors. Hiding the path keeps both endpoints
visible. Regeneration rewrites the output file and retains visibility and all
three color settings. EOF and Ctrl-C exit cleanly.

The renderer uses Unicode walls and junctions, with three columns and two rows
per cell. Color changes affect the display, not the maze or exported data.

### Output format

`OUTPUT_FILE` is overwritten with:

1. Exactly `HEIGHT` rows, each containing `WIDTH` uppercase hexadecimal digits
   (`0`–`F`), one digit per cell, ordered left to right and top to bottom.
2. One empty line.
3. Entry coordinates as `x,y`.
4. Exit coordinates as `x,y`.
5. The shortest path as a string containing only `N`, `E`, `S`, and `W`.

Every line, including the last, ends with `\n`. There are no spaces, labels, or
ANSI color codes in the output. Each digit encodes closed walls:

| Bit | Value | Direction |
| --- | --- | --- |
| 0 | 1 | North |
| 1 | 2 | East |
| 2 | 4 | South |
| 3 | 8 | West |

A set bit means closed; an unset bit means open. For example, `3` closes north
and east, and `F` closes all four walls. Configuration and footer coordinates
use `(x,y)`; maze arrays and BFS coordinates use `(row,column)`.

## Algorithms and technical choices

We chose **Sidewinder** because it is simple to understand and implement,
efficient on grids, and naturally works row by row. It fits our wall-bit
representation and was easier to debug and extend than starting with a more
complex algorithm.

Sidewinder forms horizontal runs and randomly selects northward connections.
**Union-Find** tracks connected components and completes connections around
the blocked 42 cells without introducing cycles. Shared walls are opened on
both cells.

- **Perfect mode (`PERFECT=True`):** the ordinary cells form a spanning tree,
  with no loops and exactly one path between any two ordinary cells.
- **Non-perfect mode (`PERFECT=False`):** braiding opens extra passages at dead
  ends, then a loop pass ensures at least two independent cycles. A board is
  accepted only with at most two dead ends; the four corners and centre remain
  reachable ordinary cells. Openings that create a fully open 3×3 area are
  rejected. Generation tries at most 30 layouts before reporting failure.

The 42 placement protects entry and exit, and also the corners and centre in
non-perfect mode. Interior positions are preferred, but eligible edge positions
are tried too. If none works, the pattern is omitted with a warning. Grids
without room for two loops cannot be used in non-perfect mode.

**Breadth-first search (BFS)** explores open passages using a queue, records
parent links, and reconstructs an `N/E/S/W` route. Since each step has equal
cost, the returned route is shortest in either mode.

## Reusing mazegen

`mazegen/` is the reusable package, exporting `Config`, `Parser`,
`MazeGenerator`, `solver`, and `Renderer`. Its `__init__.py` includes API
documentation. `LICENSE.md` uses the MIT license, allowing reuse and
distribution under its terms. Generation can be used without the interactive
application and does not write files or launch a display:

```python
from mazegen import Config, MazeGenerator, solver

# [width, height, entry(x,y), exit(x,y), output_file, perfect, seed]
config = Config([20, 15, (0, 0), (19, 14), "maze.txt", True, 3])
generator = MazeGenerator(config)
maze = generator._generate()  # list[list[int]], indexed as maze[y][x]
solution = solver.BFS(maze, (0, 0), (14, 19)).solve()
print(maze[0][0], solution)
```

Change the size, endpoints, mode, and seed in the `Config` list to pass custom
parameters. `_generate()` returns the maze as a row-major `list[list[int]]`
of wall-bit values; `BFS.solve()` returns a shortest direction string.
Invalid/impossible generator parameters or an unreachable BFS exit raise
`ValueError`. `Parser()._read_config("config.txt")` can read a configuration,
returning `None` after reporting a parsing/file error.

### Build and install the distributable

The package uses the `uv_build` backend configured in `pyproject.toml`. To build
a wheel from the current sources at the project root:

```sh
make install
uv run python -m build --wheel --outdir .
```

The distributable is `mazegen-0.1.0-py3-none-any.whl`. To install that root-level
wheel into a separate environment, run from the project root:

```sh
python3 -m venv /tmp/mazegen-check
/tmp/mazegen-check/bin/python -m pip install ./mazegen-0.1.0-py3-none-any.whl
```

Use that environment's Python to run the example from outside the source
directory when checking the installed package.

## Verification and maintenance

```sh
make lint
make clean
```

`lint` executes `flake8 .` and the required command:

```sh
mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

`make lint-strict` additionally provides the optional `mypy . --strict` check.
`make clean` removes Python and mypy caches. Independent unittest/project
scripts were used for edge cases and integration. The subject's
`maze_analyzer.py`, supplied in `a_maze_ing-analyzer.tgz`, was also used to
check wall coherence, connectivity, and generation-mode verdicts.

## Team and project management

### Original responsibilities

- **Akamamji:** `maze_generator.py`, `renderer.py`, and `parser.py`.
- **mhaddad:** `solver.py`, `LICENSE.md`, `Makefile`, and `pyproject.toml`.
- **Both:** shared work on `a_maze_ing.py`, which connects the components.

These are our original responsibilities, independent of later fixes or file
moves.

### Planning and evolution

We first divided the work into parsing, generation, solving, rendering, and
application integration, and made each component work independently. During
integration and subject review, configuration handling, output generation,
terminal interactions, packaging, and edge cases needed more work. Our plan
then shifted to testing the modules together and fixing compliance issues
without replacing the original algorithms.

### What worked well and what could improve

Separate modules let us work in parallel and made debugging easier. Testing
components independently helped us locate integration problems. Sharing the
wall-bit representation also kept generation, solving, rendering, and output
generation consistent.

If we restarted, we would define module interfaces earlier, especially between
the renderer, solver, and main application. We would also test subject edge
cases and packaging sooner, using an early checklist based on the PDF to
reduce late compliance work.

### Tools used

Python, uv, Make, Git,  pdb, flake8, mypy, Python unittest/project test
scripts, the Python build frontend, `maze_analyzer.py`, and ChatGPT/AI tools for explanations and review.

## Resources

- [Python deque and BFS queue support](https://docs.python.org/3/library/collections.html#collections.deque)
- [Maze generation algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Disjoint-set / Union-Find](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [union find intro](https://www.youtube.com/watch?v=ibjEGG7ylHk&t=4s)
- [Kruskal's Algorithm ](https://www.youtube.com/watch?v=JZBQLXgSGfs)
- [path Compression](https://www.youtube.com/watch?v=VHRhJWacxis)
- [Jamis Buck: Sidewinder](https://weblog.jamisbuck.org/2011/2/3/maze-generation-sidewinder-algorithm)
- [PEP 257: docstring conventions](https://peps.python.org/pep-0257/)
- [uv build backend](https://docs.astral.sh/uv/concepts/build-backend/)

### AI use

We used AI as a support tool for understanding programming and terminal-rendering
concepts, reviewing edge cases, and reviewing/refactoring code. It helped check
parser and renderer edge cases, review integration between the generator,
solver, renderer, and main application, and suggest small refactoring/compliance
improvements and testing scenarios based on the subject.

The team developed the original generator, solver, parser, renderer, and project
structure. AI mainly helped with explanations, review, testing ideas, and
identifying edge cases.
