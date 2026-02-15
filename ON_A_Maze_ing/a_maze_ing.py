#!/usr/bin/env python3
"""
Entry point for the A-Maze-ing project.

Runs the application using a config file passed as CLI argument,
or falls back to the default config inside MazeConfig.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from classes import Manager, MazeConfig


BASE_DIR: Path = Path(__file__).resolve().parent


def _resolve_config_path(arg: str) -> Path:
    """Resolve config path relative to the project directory."""
    candidate = Path(arg)
    if candidate.is_absolute():
        return candidate
    return (BASE_DIR / candidate).resolve()


def main(argv: list[str]) -> int:
    """
    Main entry point.

    Args:
        argv: Command-line arguments (excluding executable name).

    Returns:
        Exit code (0 on success, non-zero on error).
    """
    config_path: Optional[Path] = None
    if len(argv) >= 1:
        config_path = _resolve_config_path(argv[0])

    try:
        config = MazeConfig.load_config(config_path)
        app = Manager(config)
        app.run()
        return 0
    except KeyboardInterrupt:
        # graceful quit
        print("\n[SYSTEM]: Interrupted by user.")
        return 0
    except Exception as exc:
        # do not crash during review
        print(f"[ERROR]: Unhandled exception: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
