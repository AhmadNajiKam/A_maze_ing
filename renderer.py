from enum import StrEnum


class Printable(StrEnum):
    """Vertical Line ┃"""
    VLINE = "\u2503"
    """Horizontal Line ━"""
    HLINE = "\u2501"
    """Upper-Left corner ┏"""
    ULCORNER = "\u250F"
    """Upper-Right corner ┓"""
    URCORNER = "\u2513"
    """Bottom-Left corner ┗"""
    BLCORNER = "\u2517"
    """Bottom-Right corner ┛"""
    BRCORNER = "\u251B"
    """Bottom-Half cross ┳"""
    BHCROSS = "\u2533"
    """Upper-Half cross ┻"""
    UHCROSS = "\u253B"
    """Left-Half cross ┫"""
    LHCROSS = "\u252B"
    """Right-Half cross ┣"""
    RHCROSS = "\u2523"
    """Cross ╋"""
    CROSS = "\u254B"


class Renderer:
    _seed: dict[str, int] = {}

    def _load_seed(self) -> None:
        self._seed["rows"] = 21
        self._seed["cols"] = 41

    def _render_borders(self) -> None:
        row_toggle: int = 1
        for r in range(int(self._seed["rows"])):

            if r == 0:
                print(Printable.ULCORNER, end="")
                for c in range(self._seed["cols"] - 2):
                    if (c + 1) % 4 == 0:
                        print(Printable.BHCROSS, end="")
                    else:
                        print(Printable.HLINE, end="")
                print(Printable.URCORNER)

            elif r == int(self._seed["rows"]) - 1:
                print(Printable.BLCORNER, end="")
                for c in range(self._seed["cols"] - 2):
                    if (c + 1) % 4 == 0:
                        print(Printable.UHCROSS, end="")
                    else:
                        print(Printable.HLINE, end="")
                print(Printable.BRCORNER)

            else:
                if not row_toggle:
                    print(Printable.RHCROSS, end="")
                else:
                    print(Printable.VLINE, end="")
                for c in range(self._seed["cols"] - 2):
                    if (c + 1) % 4 == 0:
                        if not row_toggle:
                            print(Printable.CROSS, end="")
                        else:
                            print(Printable.VLINE, end="")
                    else:
                        if not row_toggle:
                            print(Printable.HLINE, end="")
                        else:
                            print(end=" ")
                if not row_toggle:
                    print(Printable.LHCROSS)
                else:
                    print(Printable.VLINE)
                row_toggle = not row_toggle

    def _move_cursor(self, direction: str, steps: int) -> None:

        match direction:
            case "UP":
                print(f"\x1B[{steps}A", end="")
            case "DOWN":
                print(f"\x1B[{steps}B", end="")
            case "RIGHT":
                print(f"\x1B[{steps}C", end="")
            case "LEFT":
                print(f"\x1B[{steps}D", end="")

    def render(self) -> None:
        # This is the final render function
        self._load_seed()
        self._render_borders()


def main() -> None:
    rnd = Renderer()
    rnd.render()


if __name__ == "__main__":
    main()
