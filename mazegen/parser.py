"""Read and validate KEY=VALUE maze configuration files."""

from os.path import exists, samefile
from secrets import randbits

from .config import Config


class Parser:
    """Convert a configuration file to typed settings with readable errors."""

    def _required_keys(self) -> set[str]:
        """Build mandatory keys without shared mutable data."""
        return {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}

    def parse(self, filename: str) -> Config:
        """Read settings, preserving filename and line context in errors."""
        try:
            values = self._read_values(filename)
            missing = sorted(self._required_keys() - values.keys())
            if missing:
                raise ValueError(
                    "missing mandatory keys: " + ", ".join(missing),
                )
            output_file = values["OUTPUT_FILE"]
            if exists(output_file) and samefile(filename, output_file):
                raise ValueError(
                    "OUTPUT_FILE must not overwrite the config file",
                )
            config = Config(
                width=int(values["WIDTH"]),
                height=int(values["HEIGHT"]),
                entry=self._parse_position(values["ENTRY"]),
                exit=self._parse_position(values["EXIT"]),
                output_file=output_file,
                perfect=values["PERFECT"].lower() == "true",
                seed=(int(values["SEED"]) if "SEED" in values
                      else randbits(64)),
            )
            config.validate()
            return config
        except (OSError, UnicodeError, ValueError) as error:
            raise ValueError(f"{filename}: {error}") from error

    def _read_values(self, filename: str) -> dict[str, str]:
        """Normalize keys and reject malformed or duplicate entries."""
        values: dict[str, str] = {}
        supported_keys = self._required_keys() | {"SEED"}
        with open(filename, encoding="utf-8") as file:
            for line_number, line in enumerate(file, 1):
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                try:
                    if line.count("=") != 1:
                        raise ValueError("expected one KEY=VALUE pair")
                    key, value = (part.strip() for part in line.split("="))
                    key = key.upper()
                    if key not in supported_keys:
                        raise ValueError(f"unknown key: {key}")
                    if key in values:
                        raise ValueError(f"duplicate key: {key}")
                    self._validate_value(key, value)
                    values[key] = value
                except ValueError as error:
                    raise ValueError(f"line {line_number}: {error}") from error
        return values

    def _validate_value(self, key: str, value: str) -> None:
        """Check syntax without mixing values and error sentinels."""
        if key in {"WIDTH", "HEIGHT", "SEED"}:
            if not value.isdecimal():
                raise ValueError(f"{key} must contain decimal digits")
        elif key in {"ENTRY", "EXIT"}:
            parts = value.split(",")
            if len(parts) != 2 or not all(part.isdecimal() for part in parts):
                raise ValueError(f"{key} must be nonnegative coordinates x,y")
        elif key == "PERFECT":
            if value.lower() not in {"true", "false"}:
                raise ValueError("PERFECT must be True or False")
        elif not value:
            raise ValueError("OUTPUT_FILE must not be empty")

    def _parse_position(self, value: str) -> tuple[int, int]:
        """Convert an already syntax-checked external x,y position."""
        x, y = value.split(",")
        return int(x), int(y)
