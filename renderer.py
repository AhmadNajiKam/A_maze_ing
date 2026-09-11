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
        1: Printable.UVLINE, 2: Printable.RHLINE, 3: Printable.BLCORNER,
        4: Printable.BVLINE,  5: Printable.VLINE, 6: Printable.ULCORNER,
        7: Printable.RHCROSS, 8: Printable.LHLINE, 9: Printable.BRCORNER,
        10: Printable.HLINE, 11: Printable.UHCROSS, 12: Printable.URCORNER,
        13: Printable.LHCROSS, 14: Printable.BHCROSS, 15: Printable.CROSS
    }
    _maze: list[str] = []
    _translator: dict[str, int] = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
        '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15}

    def _load_seed(self) -> None:
        self._maze: list[str] = [
            "BB913D13B",
            "AC2AC56C2",
            "C3EA97956",
            "BC3AC3A97",
            "87C696AC3",
            "855543C52",
            "C5557C556"
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
        rows: int = len(self._maze) * 2
        cols: int = len(self._maze[0]) * 3
        for r in range(rows + 1):
            # TODO: Needs some refactoring for the color codes
            if r == 0:
                print("\x1B[47;37m" + Printable.ULCORNER, end="\x1B[0m")
                for c in range(cols - 1):
                    print("\x1B[47;37m" + Printable.HLINE, end="\x1B[0m")
                print("\x1B[47;37m" + Printable.URCORNER + "\x1B[0m")

            elif r == int(rows):
                print("\x1B[47;37m" + Printable.BLCORNER, end="\x1B[0m")
                for c in range(cols - 1):
                    print("\x1B[47;37m" + Printable.HLINE, end="\x1B[0m")
                print("\x1B[47;37m" + Printable.BRCORNER + "\x1B[0m")

            else:
                print("\x1B[47;37m" + Printable.VLINE, end="\x1B[0m")
                for c in range(cols - 1):
                    print(end=" ")
                print("\x1B[47;37m" + Printable.VLINE + "\x1B[0m")
        end_coordinates: tuple[int, int] = self._cursor_position()
        return [(start_coordinates[0] + 1, start_coordinates[1]),
                end_coordinates]

    def _converter(self, character: str) -> int:
        return self._translator[character]

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
                if col == col_length - 1:
                    if self._converter(self._maze[row][col]) & Directions.SOUTH:
                        print(end=2 * Printable.HLINE)
                    continue
                if row == row_length - 1:
                    if self._converter(self._maze[row][col]) & Directions.EAST:
                        self._move_cursor((place[0] - 1, place[1] + 2))
                        print(end=Printable.VLINE)
                    continue

                if self._converter(self._maze[row][col]) & Directions.SOUTH:
                    print(end=2 * Printable.HLINE)
                else:
                    print(end="  ")
                print(end=self._decide_corner(row, col))
                self._move_cursor((place[0] - 1, place[1] + 2))
                if self._converter(self._maze[row][col]) & Directions.EAST:
                    print(end=Printable.VLINE)
                else:
                    print(end=" ")

    def _move_cursor(self, coordinates: tuple[int, int]) -> None:
        print(end=f"\x1B[{coordinates[0]};{coordinates[1]}H")

    def render(self) -> None:
        # This is the final render function
        self._load_seed()
        # coordinates: tuple[int, int] = self._cursor_position()
        coordinates: list[tuple[int, int]] = self._render_borders()
        self._draw(coordinates[0])
        # self._draw(coordinates)

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
