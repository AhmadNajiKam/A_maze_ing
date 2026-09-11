from enum import StrEnum, Enum
import termios
import sys
import tty


class Directions(int, Enum):
    """North"""
    NORTH = 0b0001
    """East"""
    EAST = 0b0010
    """South"""
    SOUTH = 0b0100
    """West"""
    WEST = 0b1000


class Printable(StrEnum):
    """Vertical Line ┃"""
    VLINE = "\u2503"
    """Horizontal Line ━"""
    HLINE = "\u2501"
    """Left Vertical Line"""
    LVLINE = "\u258F"
    """Right Vertical Line"""
    RVLINE = "\u2595"
    """Upper Horizontal Line"""
    UHLINE = "\u2594"
    """Bottom Horizontal Line"""
    BHLINE = "\u2581"
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
    _maze: list[str] = []
    _translator: dict[str, int] = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
        '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15}

    def _load_seed(self) -> None:
        self._maze: list[str] = ["B9153B9153D1795513B955157",
                                 "AAC3AC6A94169457A86C3BC53",
                                 "AABAC53AAFAFAFFFAE956853A",
                                 "AAAA93C6AFEF857FC543D2D2A",
                                 "AC2C6C3D2FFFAFFFB93C3C3AA",
                                 "83AD13C3AD3FAFD52EAD456EA",
                                 "AAA96A96C56FAFFFC3C555556",
                                 "AC6ABAA93953A953943D55153",
                                 "C556C6C6C47C46D46D45556D6"
                                 ]

    def _cursor_position(self) -> tuple[int, int]:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            print(end="\x1b[6n", flush=True)

            response = ""
            while not response.endswith("R"):
                response += sys.stdin.read(1)

            row, col = response[2:-1].split(";")
            return int(row), int(col)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def _render_borders(self) -> list[tuple[int, int]]:
        start_coordinates: tuple[int, int] = self._cursor_position()
        rows: int = len(self._maze)
        cols: int = len(self._maze[0])
        for r in range(rows + 1):
            # TODO: Needs some refactoring for the color codes
            if r == 0:
                print("\x1B[107;97m" + Printable.ULCORNER, end="\x1B[0m")
                for c in range(cols + 1):
                    print("\x1B[107;97m" + Printable.HLINE, end="\x1B[0m")
                print("\x1B[107;97m" + Printable.URCORNER + "\x1B[0m")

            elif r == int(rows):
                print("\x1B[107;97m" + Printable.BLCORNER, end="\x1B[0m")
                for c in range(cols + 1):
                    print("\x1B[107;97m" + Printable.HLINE, end="\x1B[0m")
                print("\x1B[107;97m" + Printable.BRCORNER + "\x1B[0m")

            else:
                print("\x1B[107;97m" + Printable.VLINE, end="\x1B[0m")
                for c in range(cols + 1):
                    print(end=" ")
                print("\x1B[107;97m" + Printable.VLINE + "\x1B[0m")
        end_coordinates: tuple[int, int] = self._cursor_position()
        return [start_coordinates, end_coordinates]

    def _converter(self, character: str) -> int:
        return self._translator[character]

    def _put_cell(self, value: int) -> None:
        pass

    def _draw(self, start_coordinates: tuple[int, int]) -> None:
        for row in range(len(self._maze)):
            multiplier: int = 0
            for col in range(len(self._maze[0])):
                self._move_cursor(
                    (start_coordinates[0] + row + 1,
                     start_coordinates[1] + col + 1 + multiplier * 2))
                print(end=Printable.BHLINE)
                print(end=Printable.BHLINE)
                if row == 0:
                    print(end=Printable.BHLINE)
                self._move_cursor(
                    (start_coordinates[0] + row + 2,
                     start_coordinates[1] + col + 3 + multiplier * 2))
                print(end=Printable.VLINE)
                print(end="\x1b[0m")
                multiplier += 1

    def _move_cursor(self, coordinates: tuple[int, int]) -> None:
        print(end=f"\x1B[{coordinates[0]};{coordinates[1]}H")

    def render(self) -> None:
        # This is the final render function
        self._load_seed()
        coordinates: list[tuple[int, int]] = self._render_borders()
        self._draw(coordinates[0])
        self._draw(coordinates[0])

        # To restore the cursor to the right place
        print(end=f"\x1B[{coordinates[1][0]};{coordinates[1][1]}H")
        # print(end="\x1B7")
        # self._draw()
        # print(end="\x1B8")


def main() -> None:
    rnd = Renderer()
    rnd.render()


if __name__ == "__main__":
    main()
