"""
Configuration management for the maze generation application.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any


class MazeConfig:
    """Holds configuration settings for maze generation.

        This class handles loading settings from external files,
        validating the data,
        and providing a structured object to access configuration
        parameters like
        dimensions, entry/exit points, and algorithm constraints.

        Attributes:
            maze_width (int): The width of the maze grid.
            maze_height (int): The height of the maze grid.
            maze_entry (List[int]): Coordinates [x, y] for the starting point.
            maze_exit (List[int]): Coordinates [x, y] for the exit point.
            output_file_name (str): Filename for saving the generated maze.
            maze_perfect (bool): If True, generates a perfect maze (no loops).
                If False, allows loops (braid maze).
        """
    DEFAULT_CONFIG_NAME = "default_config.txt"

    # Maps keys found in the config file to class attribute names.
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
                 output_file: str, perfect: bool) -> None:
        """Initializes a MazeConfig instance.

        Args:
            maze_width (int): Width of the maze.
            maze_height (int): Height of the maze.
            maze_entry (List[int]): [x, y] coordinates for start.
            maze_exit (List[int]): [x, y] coordinates for exit.
            output_file (str): Output filename.
            perfect (bool): Loop generation flag.
        """
        self.maze_width = maze_width
        self.maze_height = maze_height
        self.maze_entry = maze_entry
        self.maze_exit = maze_exit
        self.output_file_name = output_file
        self.maze_perfect = perfect

    def get_info(self) -> str:
        """Returns a string representation of the configuration.

        Returns:
            str: Dictionary string of instance attributes.
        """
        return str(self.__dict__)

    @classmethod
    def load_config(cls,
                    user_file_name: Optional[Path] = None) -> "MazeConfig":
        """Attempts to load configuration from a file.

        Tries to load the configuration from the provided user
        filename first.
        If that fails or is not provided, falls back to the default
        configuration file located in the project root.

        Args:
            user_file_name (Optional[Path]): Path to the user-provided
            config file.

        Returns:
            MazeConfig: An initialized configuration object.

        Raises:
            SystemExit: If no valid configuration file can be loaded.
        """
        config_candidates = []
        if user_file_name:
            config_candidates.append(user_file_name)

        # Assuming the structure is
        # classes/maze_config.py -> root/default_config.txt
        default_path = Path(__file__).parent.parent / cls.DEFAULT_CONFIG_NAME
        config_candidates.append(default_path.resolve())

        for path in config_candidates:
            # print(f"Loadin configuration file: {path}")  # Debug
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
        """Checks if a file exists at the given path."""
        return file_name.is_file()

    @classmethod
    def _read_file(cls, file_path: Path) -> Dict[str, Any]:
        """Parses a configuration file.

        Reads line by line, splitting by '='. Converts values to appropriate
        types (int, list, bool) based on the content.

        Args:
            file_path (Path): Path to the file to read.

        Returns:
            Dict[str, Any]: A dictionary of parsed configuration data with
            mapped keys. Returns an empty dict on failure.
        """
        data = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        raw_key, value = line.strip().split("=", 1)
                        # Clean up whitespace around the value
                        value = value.strip()

                        # Map file key (e.g. WIDTH) to class key
                        # (e.g. maze_width)
                        if raw_key not in cls.KEY_MAPPING:
                            continue

                        key = cls.KEY_MAPPING[raw_key]

                        if "," in value:
                            data[key] = [int(x) for x in value.split(",")]
                        elif value.isdigit():
                            data[key] = int(value)
                        elif value.lower() == "false":
                            data[key] = False
                        elif value.lower() == "true":
                            # FIX: Was 'False' in original code, fixed to True
                            data[key] = False
                        else:
                            data[key] = value
            return data
        except Exception as e:
            print(f"Exception on riding {file_path}: {e}")
            return {}

    @staticmethod
    def _config_verify(data: Dict[str, Any]) -> bool:
        """Validates that the parsed data contains all required fields.

        Args:
            data (Dict[str, Any]): The dictionary parsed from the file.

        Returns:
            bool: True if data is valid, False otherwise.
        """
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
