"""
Main entry point for the A-Maze-Ing application.

This script serves as the bootstrap for the maze generation program.
It handles command-line arguments to locate the configuration file,
initializes the core components, and starts the main application loop.
"""

import sys
from pathlib import Path
from classes import MazeConfig, Manager

BASE_DIR = Path(__file__).resolve().parent


def main():
    """Initializes and runs the maze application.

        Reads the configuration filename from command-line arguments,
        loads the corresponding config object, and triggers the Manager
        to start the application life cycle.

        Usage:
            python a_maze_ing.py <config_filename>

        Example:
            python a_maze_ing.py config.json
        """
    if len(sys.argv) == 2:
        con_file_name = sys.argv[1]
        full_config_path = BASE_DIR / con_file_name
        configs = MazeConfig.load_config(full_config_path)
        app = Manager(configs)
        app.run()


if __name__ == "__main__":
    main()
