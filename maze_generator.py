from parser import Config
import random


class MazeGenerator:
    def __init__(self, config: Config) -> None:
        self._maze: list[list[int]] = []
        self._config: Config = config
        for i in range(self._config._HEIGHT):
            self._maze.append([])
            for j in range(self._config._WIDTH):
                self._maze[i].append(15)

        for i in range(config._HEIGHT):
            for j in range(config._WIDTH):
                print(end=str(self._maze[i][j]) + " ")
            print()

    def _generate(self) -> None:
        directions: list[str] = ["RIGHT", "UP"]
        run_set: list[tuple[int, int]]
        i: int = 0
        j: int = 1
        run_set = [self._maze[i][j]]
        while (i < self._config._HEIGHT
               and j < self._config._WIDTH):
            chosen_dir: str = random.choice(directions)
            if chosen_dir == "RIGHT":
                if j < self._config._WIDTH - 1:
                    j += 1
                else:
                    run_set = []
                    j = 0
                    i += 1
                if len(run_set) != 0:

                run_set.append(self._maze[i][j])

            else:


if __name__ == "__main__":
    config = Config([20, 20, (0, 0), (10, 5), "output.txt", True])
    mazeGenerator = MazeGenerator(config)
    mazeGenerator._generate()
