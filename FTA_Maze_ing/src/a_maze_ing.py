import sys
from pathlib import Path
from classes import MazeConfig, Manager

BASE_DIR = Path(__file__).resolve().parent


def main():
    if len(sys.argv) == 2:
        con_file_name = sys.argv[1]
        full_config_path = BASE_DIR / con_file_name
        configs = MazeConfig.load_config(full_config_path)
        app = Manager(configs)
        app.run()


if __name__ == "__main__":
    main()
