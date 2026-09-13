from typing import Any


class Config:
    def __init__(self, values: list[Any]) -> None:

        self._WIDTH: int = values[0]
        self._HEIGHT: int = values[1]
        self._ENTRY: tuple[int, int] = values[2]
        self._EXIT: tuple[int, int] = values[3]
        self._OUTPUT_FILE: str = values[4]
        self._PERFECT: bool = values[5]


class Parser:
    def _parse_engine(self, key: str, value: str) -> Any:
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
                if value.lower() != "true" and value.lower() != "false":
                    return -1
                else:
                    return bool(value)
            case "OUTPUT_FILE":
                return value
            case _:
                return -1

    def _get_key_value(self, line: str) -> tuple[str, str]:
        unnormalized_line: list[str] = line.replace("\n", "").split("=")
        if len(unnormalized_line) != 2:
            print(f"{line} is syntactically wrong, write KEY=VALUE pair.")
            return (-1, -1)
        key: str = unnormalized_line[0].upper()
        value: str = unnormalized_line[1]
        if self._parse_engine(key, value) == -1:
            return (-1, -1)
        return (key, value)

    def _read_config(self, config_file: str) -> Config | None:

        try:
            with open(config_file, "r") as file:
                config_array: list[Any] = []
                for line in file:
                    kv: tuple[str, str] = self._get_key_value(line)
                    if self._get_key_value(line)[0] != -1:
                        config_array.append(self._parse_engine(kv[0], kv[1]))
                    else:
                        print("Configuration error")
                        return
                config = Config(config_array)
                return config

        except FileNotFoundError:
            print("The file does not exist.")

        except PermissionError:
            print("You don't have permission to read the file.")

        except OSError as e:
            print(f"Operating system error: {e}")


def main() -> None:
    parser = Parser()
    print(parser._read_config("config.txt"))


if __name__ == "__main__":
    main()
