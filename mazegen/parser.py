from random import randint

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
)


class Config(BaseModel):
    model_config = ConfigDict(extra="forbid")

    width: int = Field(gt=0)
    height: int = Field(gt=0)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str = Field(min_length=1)
    perfect: bool
    seed: int | None = None

    @field_validator("entry", "exit", mode="before")
    @classmethod
    def parse_coordinates(
        cls,
        value: object,
    ) -> tuple[int, int]:
        if not isinstance(value, str):
            raise ValueError("coordinates must be x,y")

        parts = value.split(",")

        if len(parts) != 2:
            raise ValueError("coordinates must be x,y")

        x, y = parts

        if not x.isdigit() or not y.isdigit():
            raise ValueError("coordinates must contain integers")

        return int(x), int(y)


class Parser:
    def _get_key_value(self, line: str) -> tuple[str, str]:
        parts = line.strip().split("=")

        if len(parts) != 2:
            raise ValueError("expected one KEY=VALUE pair")

        key = parts[0].strip().lower()
        value = parts[1].strip()

        return key, value

    def _read_config(self, config_file: str) -> Config | None:
        try:
            values: dict[str, str] = {}

            with open(config_file, "r", encoding="utf-8") as file:
                for number, line in enumerate(file, 1):
                    if not line.strip() or line.lstrip().startswith("#"):
                        continue

                    try:
                        key, value = self._get_key_value(line)

                        if key in values:
                            raise ValueError(f"duplicate key: {key}")

                        values[key] = value

                    except ValueError as error:
                        raise ValueError(
                            f"line {number}: {error}"
                        ) from error

            config = Config.model_validate(values)

            if config.seed is None:
                config.seed = randint(1, 1000000)
                print(f"Generated seed: {config.seed}")

            return config

        except (OSError, UnicodeError, ValueError, ValidationError) as error:
            print(f"Error: {config_file}: {error}")
            return None
