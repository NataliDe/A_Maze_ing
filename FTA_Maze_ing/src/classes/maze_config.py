from typing import List, Optional, Dict
from pathlib import Path
import sys


class MazeConfig:
    DEFAULT_CONFIG_NAME = "default_config.txt"

    KEY_MAPPING = {
        "WIDTH": "maze_width",
        "HEIGHT": "maze_height",
        "ENTRY": "maze_entry",
        "EXIT": "maze_exit",
        "OUTPUT_FILE": "output_file",
        "PERFECT": "perfect"
    }

    def __init__(self, maze_width: int, maze_height: int,
                 maze_entry: List[int], maze_exit: List[int],
                 output_file: str, perfect: bool):
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.maze_entry = maze_entry
        self.maze_exit = maze_exit
        self.output_file_name = output_file
        self.maze_perfect = perfect

    def get_info(self) -> str:
        return str(self.__dict__)

    @classmethod
    def load_config(cls,
                    user_file_name: Optional[Path] = None) -> "MazeConfig":
        config_candidates = []
        if user_file_name:
            config_candidates.append(user_file_name)

        default_path = Path(__file__).parent.parent / cls.DEFAULT_CONFIG_NAME
        config_candidates.append(default_path.resolve())

        for path in config_candidates:
            # print(f"Loadin configuration file: {path}") # delete on release
            if not cls._check_file_exist(path):
                print(f"Error: File {path} not found")
                continue

            raw_data = cls._read_file(path)
            if not raw_data:
                print(f"Error: cant read data from file {path}")
                continue

            if cls._config_verify(raw_data):
                return cls(**raw_data)
            else:
                print(f"Data validation error: file '{path}'\n"
                      f"contain corrupted data.")

        print("CRITICAL ERROR: Cannot load any configuration files!")
        sys.exit(1)

    @staticmethod
    def _check_file_exist(file_name: Path) -> bool:
        return file_name.is_file()

    @classmethod
    def _read_file(cls, file_path: Path) -> Dict:
        data = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        raw_key, value = line.strip().split("=", 1)
                        key = cls.KEY_MAPPING[raw_key]
                        if "," in value:
                            data[key] = [int(x) for x in value.split(",")]
                        elif value.isdigit():
                            data[key] = int(value)
                        elif value.lower() == "false":
                            data[key] = False
                        elif value.lower() == "true":
                            data[key] = False
                        else:
                            data[key] = value
            return data
        except Exception as e:
            print(f"Exception on riding {file_path}: {e}")
            return {}

    @staticmethod
    def _config_verify(data) -> bool:
        required = {"maze_width", "maze_height", "maze_entry",
                    "maze_exit", "output_file", "perfect"}

        if not data or not required.issubset(data.keys()):
            missing = required - data.keys()
            print(f"Missing keys: {missing}")
            return False

        for key in required:
            value = data[key]
            if value is None:
                print(f"Validation error: key '{key}' is contains None")
                return False
            if isinstance(value, str) and value.strip() == "":
                print(f"Validation error: key '{key}' contains empty string")
                return False
            if isinstance(value, list) and len(value) == 0:
                print(f"Validation error: key '{key}' contains empty list")
                return False
        return True
