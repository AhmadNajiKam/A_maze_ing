"""Named ANSI colors and validated 24-bit custom colors."""

from dataclasses import dataclass
from enum import IntEnum
import re


class ForegroundColor(IntEnum):
    """Standard ANSI foreground colors for walls and endpoint labels."""

    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    BRIGHT_WHITE = 97


class BackgroundColor(IntEnum):
    """Standard ANSI background colors for cell interiors."""

    RED = 41
    GREEN = 42
    YELLOW = 43
    BLUE = 44
    MAGENTA = 45
    CYAN = 46
    WHITE = 47


@dataclass(frozen=True)
class RGBColor:
    """An RGB color with its foreground/background rendering mode."""

    red: int
    green: int
    blue: int
    background: bool = False

    def __post_init__(self) -> None:
        """Keep each channel within the true-color range."""
        if any(not 0 <= channel <= 255 for channel in (
            self.red, self.green, self.blue,
        )):
            raise ValueError("RGB channels must be between 0 and 255")

    def __str__(self) -> str:
        """Return ANSI parameters without the escape-sequence wrapper."""
        mode = 48 if self.background else 38
        return f"{mode};2;{self.red};{self.green};{self.blue}"


def parse_color(value: str, *, background: bool = False) -> int | RGBColor:
    """Accept a named color or an exact #RRGGBB hexadecimal value."""
    value = value.strip()
    palette = BackgroundColor if background else ForegroundColor
    name = value.upper()
    if name in palette.__members__:
        return palette[name]
    if re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        return RGBColor(
            int(value[1:3], 16), int(value[3:5], 16),
            int(value[5:7], 16), background=background,
        )
    raise ValueError("Enter a listed color name or a hex code like #FF8800.")
