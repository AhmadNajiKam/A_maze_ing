

class Renderer:
    seed: dict[str, int] = {}

    def load_seed(self) -> None:
        self.seed["rows"] = 21
        self.seed["cols"] = 21

    def render(self) -> None:
        for r in range(int(self.seed["rows"] / 2)):
            if r == 0:
                print("\u250F", end="")
                for c in range(self.seed["cols"] - 2):
                    if c % 2:
                        print("\u2533", end="")
                    else:
                        print("\u2501", end="")
                print("\u2513")

            elif r == int(self.seed["rows"] / 2) - 1:
                print("\u2517", end="")
                for c in range(self.seed["cols"] - 2):
                    if c % 2:
                        print("\u253B", end="")
                    else:
                        print("\u2501", end="")
                print("\u251B")

            else:
                print("\u2523", end="")
                for c in range(self.seed["cols"] - 2):
                    if c % 2:
                        print("\u254B", end="")
                    else:
                        print(end="\u2501")
                print("\u252B")


def main() -> None:
    rnd = Renderer()
    rnd.load_seed()
    rnd.render()


if __name__ == "__main__":
    main()
