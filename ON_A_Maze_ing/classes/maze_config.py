"""
Maze configuration loader.

Reads key/value pairs from a config file and validates required fields.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class MazeConfig:
    """
    Configuration for maze generation and output.
    """

    DEFAULT_CONFIG_NAME: str = "config.txt"

    KEY_MAPPING: Dict[str, str] = {
        "WIDTH": "maze_width",
        "HEIGHT": "maze_height",
        "ENTRY": "maze_entry",
        "EXIT": "maze_exit",
        "OUTPUT_FILE": "output_file",
        "PERFECT": "perfect",
    }

    def __init__(
        self,
        maze_width: int,
        maze_height: int,
        maze_entry: List[int],
        maze_exit: List[int],
        output_file: str,
        perfect: bool,
    ) -> None:
        self.maze_width: int = maze_width
        self.maze_height: int = maze_height
        self.maze_entry: List[int] = maze_entry
        self.maze_exit: List[int] = maze_exit
        self.output_file_name: str = output_file
        self.maze_perfect: bool = perfect

    @classmethod
    def load_config(
            cls, user_file_name: Optional[Path] = None) -> "MazeConfig":
        """
        Load configuration from user file or fallback
        to DEFAULT_CONFIG_NAME in project root.
        """
        candidates: List[Path] = []
        if user_file_name is not None:
            candidates.append(user_file_name)

        default_path = (Path.cwd() / cls.DEFAULT_CONFIG_NAME).resolve()
        candidates.append(default_path)

        for path in candidates:
            if not path.is_file():
                print(f"[ERROR]: Config file not found: {path}")
                continue

            raw_data = cls._read_file(path)
            if not raw_data:
                print(f"[ERROR]: Cannot read config data from: {path}")
                continue

            if cls._config_verify(raw_data):
                return cls(**raw_data)

            print(f"[ERROR]: Config validation failed for file: {path}")

        print("[CRITICAL]: Cannot load any configuration files!")
        sys.exit(1)

    @classmethod
    def _read_file(cls, file_path: Path) -> Dict[str, Any]:
        """
        Read config file into a dict of constructor args.
        """
        data: Dict[str, Any] = {}
        try:
            with file_path.open("r", encoding="utf-8") as handle:
                for raw_line in handle:
                    line = raw_line.strip()

                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue

                    raw_key, raw_value = line.split("=", 1)
                    raw_key = raw_key.strip().upper()
                    raw_value = raw_value.strip()

                    if raw_key not in cls.KEY_MAPPING:
                        # ignore unknown keys instead of failing
                        continue

                    key = cls.KEY_MAPPING[raw_key]
                    data[key] = cls._parse_value(raw_value)

            return data
        except (OSError, ValueError) as exc:
            print(f"[ERROR]: Failed reading config '{file_path}': {exc}")
            return {}

    @staticmethod
    def _parse_value(value: str) -> Any:
        if "," in value:
            parts = [p.strip() for p in value.split(",")]
            return [int(p) for p in parts]

        if value.isdigit():
            return int(value)

        low = value.lower()
        if low == "true":
            return True
        if low == "false":
            return False

        return value

    @staticmethod
    def _config_verify(data: Dict[str, Any]) -> bool:
        required = {
            "maze_width",
            "maze_height",
            "maze_entry",
            "maze_exit",
            "output_file",
            "perfect",
        }

        if not required.issubset(data.keys()):
            missing = required - set(data.keys())
            print(f"[ERROR]: Missing keys: {missing}")
            return False

        width = data["maze_width"]
        height = data["maze_height"]
        entry = data["maze_entry"]
        exit_ = data["maze_exit"]
        out_file = data["output_file"]
        perfect = data["perfect"]

        if not isinstance(width, int) or width <= 0:
            print("[ERROR]: WIDTH must be a positive integer")
            return False
        if not isinstance(height, int) or height <= 0:
            print("[ERROR]: HEIGHT must be a positive integer")
            return False

        if not isinstance(entry, list) or len(entry) != 2:
            print("[ERROR]: ENTRY must be in format x,y")
            return False
        if not isinstance(exit_, list) or len(exit_) != 2:
            print("[ERROR]: EXIT must be in format x,y")
            return False

        try:
            ex, ey = int(entry[0]), int(entry[1])
            gx, gy = int(exit_[0]), int(exit_[1])
        except (TypeError, ValueError):
            print("[ERROR]: ENTRY/EXIT must be integers")
            return False

        if not (0 <= ex < width and 0 <= ey < height):
            print("[ERROR]: ENTRY is out of bounds")
            return False
        if not (0 <= gx < width and 0 <= gy < height):
            print("[ERROR]: EXIT is out of bounds")
            return False

        if not isinstance(out_file, str) or not out_file.strip():
            print("[ERROR]: OUTPUT_FILE must be a non-empty string")
            return False
        if not isinstance(perfect, bool):
            print("[ERROR]: PERFECT must be true/false")
            return False

        return True
