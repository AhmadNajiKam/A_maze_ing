"""Read keyed maze configuration while retaining the original Config API."""

from secrets import randbits
from typing import Any


class Config:
    """Store width, height, endpoints, output, mode and seed in that order."""

    def __init__(self, config_array: list[Any]) -> None:
        """Store the seven values supplied by the parser or reusable client."""
        self._WIDTH: int = config_array[0]
        self._HEIGHT: int = config_array[1]
        self._ENTRY: tuple[int, int] = config_array[2]
        self._EXIT: tuple[int, int] = config_array[3]
        self._OUTPUT_FILE: str = config_array[4]
        self._PERFECT: bool = config_array[5]
        self._SEED: int = config_array[6]


class Parser:
    """Validate KEY=VALUE configuration files and report readable errors."""

    def _parse_engine(self, key: str, value: str) -> Any:
        """Convert one supported value; return -1 for an invalid value/key."""
        match key:
            case "WIDTH" | "HEIGHT":
                if value.isdigit() == 0:
                    return -1
                else:
                    return int(value)
            case "ENTRY" | "EXIT":
                values: list[str] = value.split(",")
                if (len(values) != 2 or values[0].isdigit() == 0
                        or values[1].isdigit() == 0):
                    return -1
                else:
                    return (int(values[0]), int(values[1]))
            case "PERFECT":
                if value.lower() == "true":
                    return True
                elif value.lower() == "false":
                    return False
                return -1
            case "SEED":
                if value.isdigit() == 0:
                    return -1
                else:
                    return int(value)
            case "OUTPUT_FILE":
                return value if value else -1
            case _:
                return -1

    def _get_key_value(self, line: str) -> tuple[str, str]:
        """Return a normalized pair or raise ValueError for invalid syntax."""
        unnormalized_line: list[str] = line.strip().split("=")
        if len(unnormalized_line) != 2:
            raise ValueError("expected one KEY=VALUE pair")
        key: str = unnormalized_line[0].strip().upper()
        value: str = unnormalized_line[1].strip()
        if self._parse_engine(key, value) == -1:
            raise ValueError(f"invalid key or value: {key}={value}")
        return (key, value)

    def _read_config(self, config_file: str) -> Config | None:
        """Read a file into Config; print an error and return None on failure.

        Keys may appear in any order. SEED is optional; all six subject keys
        are required. Comments and blank lines do not contribute values.
        """
        required = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",
                    "PERFECT")
        try:
            with open(config_file, "r", encoding="utf-8") as file:
                values: dict[str, Any] = {}
                for number, line in enumerate(file, 1):
                    if not line.strip() or line.lstrip().startswith("#"):
                        continue
                    try:
                        key, value = self._get_key_value(line)
                        if key in values:
                            raise ValueError(f"duplicate key: {key}")
                        values[key] = self._parse_engine(key, value)
                    except ValueError as error:
                        raise ValueError(f"line {number}: {error}") from error
            missing = [key for key in required if key not in values]
            if missing:
                raise ValueError(
                    "missing mandatory keys: " + ", ".join(missing)
                )
            if "SEED" not in values:
                values["SEED"] = randbits(64)
            config_array = [values[key] for key in required]
            config_array.append(values["SEED"])
            return Config(config_array)
        except (OSError, UnicodeError, ValueError) as error:
            print(f"Error: {config_file}: {error}")
            return None
