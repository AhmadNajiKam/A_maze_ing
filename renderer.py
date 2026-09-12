from enum import StrEnum, Enum
from os import system
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
    """Upper Vertical Line ╹"""
    UVLINE = "\u2579"
    """Bottom Vertical Line ╻"""
    BVLINE = "\u257B"
    """Left Horizontal Line╸"""
    LHLINE = "\u2578"
    """Right Horizontal Line╺"""
    RHLINE = "\u257A"
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
    _corner: dict[int, Printable] = {
        0: " ", 1: Printable.UVLINE, 2: Printable.RHLINE,
        3: Printable.BLCORNER, 4: Printable.BVLINE,  5: Printable.VLINE,
        6: Printable.ULCORNER, 7: Printable.RHCROSS, 8: Printable.LHLINE,
        9: Printable.BRCORNER, 10: Printable.HLINE, 11: Printable.UHCROSS,
        12: Printable.URCORNER, 13: Printable.LHCROSS, 14: Printable.BHCROSS,
        15: Printable.CROSS
    }
    _maze: list[str] = []
    _strtohex: dict[str, int] = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
        '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15}

    def _load_maze(self) -> None:
        self._maze: list[str] = [
            "BBD7D3FD3BFBFBF",
            "C6953A93AC1692F",
            "D56BAAAAC3C3AC7",
            "F93C6AC6D2BAA97",
            "D6C552B916AC687",
            "B9553AAEC5697AB",
            "EC53C6C5555692E",
            "D156955139556AF",
            "FA93853AC6953C7",
            "D6AC692AD3C3A97",
            "D5453EAC56946C7",
            "D553C785396953B",
            "B97A916946D692E",
            "EC3AAC3C55556C7",
            "D7EEEFED7D7FD7F"]

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
        rows: int = len(self._maze) * 2
        cols: int = len(self._maze[0]) * 3
        for r in range(rows + 1):
            # TODO: Needs some refactoring for the color codes
            if r == 0:
                print(end=Printable.ULCORNER)
                for c in range(cols - 1):
                    print(end=Printable.HLINE)
                print(Printable.URCORNER)

            elif r == int(rows):
                print(end=Printable.BLCORNER)
                for c in range(cols - 1):
                    print(end=Printable.HLINE)
                print(Printable.BRCORNER)

            else:
                print(end=Printable.VLINE)
                for c in range(cols - 1):
                    print(end=" ")
                print(Printable.VLINE)
        end_coordinates: tuple[int, int] = self._cursor_position()
        return [(start_coordinates[0] + 1, start_coordinates[1]),
                end_coordinates]

    def _converter(self, character: str) -> int:
        return self._strtohex[character]

    def _decide_corner(self, row: int, col: int) -> str:
        hex_value: int = self._converter(self._maze[row][col])
        hex_value_diagonal: int = self._converter(self._maze[row + 1][col + 1])
        total: int = 0
        if hex_value & Directions.EAST:
            total += 1
        if hex_value & Directions.SOUTH:
            total += 8
        if hex_value_diagonal & Directions.NORTH:
            total += 2
        if hex_value_diagonal & Directions.WEST:
            total += 4
        return self._corner[total]

    def _draw(self, start_coordinates: tuple[int, int]) -> None:
        col_length = len(self._maze[0])
        row_length = len(self._maze)
        for row in range(row_length):
            for col in range(col_length):
                if (col == col_length - 1
                        and row == row_length - 1):
                    continue
                place: tuple[int, int] = (
                    start_coordinates[0] + 1 + row * 2,
                    start_coordinates[1] + 1 + (col * 3))
                self._move_cursor(place)
                if self._converter(self._maze[row][col]) & Directions.SOUTH:
                    if row != row_length - 1:
                        if col == 0:
                            self._move_cursor((place[0], place[1] - 1))
                            print(end=Printable.RHCROSS)
                            print(end=2 * Printable.HLINE)
                        elif col == col_length - 1:
                            print(end=2 * Printable.HLINE)
                            print(end=Printable.LHCROSS)
                        else:
                            print(end=2 * Printable.HLINE)
                else:
                    print(end="  ")

                if row != row_length - 1 and col != col_length - 1:
                    print(end=self._decide_corner(row, col))
                self._move_cursor((place[0] - 1, place[1] + 2))

                if self._converter(self._maze[row][col]) & Directions.EAST:
                    print(end=Printable.VLINE)
                    if col != col_length - 1:
                        if row == 0:
                            self._move_cursor((place[0] - 2, place[1] + 2))
                            print(end=Printable.BHCROSS)
                        elif row == row_length - 1:
                            self._move_cursor((place[0], place[1] + 2))
                            print(end=Printable.UHCROSS)
                else:
                    print(end=" ")

    def _move_cursor(self, coordinates: tuple[int, int]) -> None:
        print(end=f"\x1B[{coordinates[0]};{coordinates[1]}H")

    def render(self) -> None:
        # Clear the terminal before drawing
        system('clear')
        self._load_maze()
        coordinates: list[tuple[int, int]] = self._render_borders()
        self._draw(coordinates[0])

        # Restore the cursor to the right place
        print(end=f"\x1B[{coordinates[1][0]};{coordinates[1][1]}H")


def main() -> None:
    rnd = Renderer()
    rnd.render()


if __name__ == "__main__":
    main()
