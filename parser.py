from typing import Any


class Config:
    def __init__(self, config_array: list[Any]) -> None:
        self._WIDTH: int = config_array[0]
        self._HEIGHT: int = config_array[1]
        self._ENTRY: tuple[int, int] = config_array[2]
        self._EXIT: tuple[int, int] = config_array[3]
        self._OUTPUT_FILE: str = config_array[4]
        self._PERFECT: bool = config_array[5]
        self._SEED: int = config_array[6]


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
                return value
            case _:
                return -1

    def _get_key_value(self, line: str) -> tuple[str, str]:
        unnormalized_line: list[str] = line.replace("\n", "").split("=")
        if len(unnormalized_line) != 2:
            print(f"{line} is syntactically wrong, write KEY=VALUE pair.")
            return ("", "")
        key: str = unnormalized_line[0].upper()
        value: str = unnormalized_line[1]
        if self._parse_engine(key, value) == -1:
            return ("", "")
        return (key, value)

    def _read_config(self, config_file: str) -> Config | None:

        try:
            with open(config_file, "r") as file:
                config_array: list[Any] = []
                for line in file:
                    kv: tuple[str, str] = self._get_key_value(line)
                    if self._get_key_value(line)[0] != "":
                        config_array.append(self._parse_engine(kv[0], kv[1]))
                    else:
                        print("Configuration error")
                        return None
                config = Config(config_array)

        except FileNotFoundError:
            print("The file does not exist.")

        except PermissionError:
            print("You don't have permission to read the file.")

        except OSError as e:
            print(f"Operating system error: {e}")
        return config
