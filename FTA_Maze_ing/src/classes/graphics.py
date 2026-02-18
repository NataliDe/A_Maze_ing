"""
Handles the visual representation of the maze components.
"""

from typing import Dict, Tuple
from .cell import Cell


class Graphics:
    """Manages the visual styles and themes for rendering the maze.

    This class encapsulates the logic for converting abstract Cell objects
    into specific characters (ASCII or Unicode box-drawing) and applying
    ANSI color codes based on selected themes.

    Attributes:
        current_style_name (str): The key of the currently active symbol style.
        current_theme_name (str): The key of the currently active color theme.
        show_path (bool): Toggles the visibility of the solution path.
    """

    # Dictionary mapping connection tuples
    # (North, East, South, West) to characters.
    # Key format: (North_Open, East_Open, South_Open, West_Open)
    SYMBOLS_STYLES: Dict[str, Dict[Tuple[bool, bool, bool, bool], str]] = {
        "uni": {
            # (Norse, East, South, West): "char"
            (True, False, False, False): "╨",
            (False, True, False, False): "╞",
            (False, False, True, False): "╥",
            (False, False, False, True): "╡",

            (True, False, True, False): "║",
            (False, True, False, True): "═",

            (False, False, False, False): "░",
            (True, True, True, True): "╬",

            (False, False, True, True): "╗",
            (False, True, True, False): "╔",
            (True, False, False, True): "╝",
            (True, True, False, False): "╚",

            (True, True, False, True): "╩",
            (False, True, True, True): "╦",
            (True, False, True, True): "╣",
            (True, True, True, False): "╠",
        },
        "ascii": {
            (True, False, False, False): "V",
            (False, True, False, False): "<",
            (False, False, True, False): "^",
            (False, False, False, True): ">",

            (True, False, True, False): "|",
            (False, True, False, True): "-",

            (False, False, False, False): "?",
            (True, True, True, True): "+",

            (False, False, True, True): "7",
            (False, True, True, False): "r",
            (True, False, False, True): "J",
            (True, True, False, False): "L",

            (True, True, False, True): "U",
            (False, True, True, True): "T",
            (True, False, True, True): "{",
            (True, True, True, False): "}",
        },
    }

    # Dictionary mapping semantic names to ANSI color codes.
    COLORS_STYLES: Dict[str, Dict[str, str]] = {
        # 1. Midnight
        "midnight": {
            "WALL": "\033[90m",  # Gray
            "PATH": "\033[97m",  # White
            "START": "\033[94m",  # Blue
            "END": "\033[92m",  # Green
            "RESET": "\033[0m",
        },

        # 2. Sunset
        "sunset": {
            "WALL": "\033[31m",  # Red
            "PATH": "\033[93m",  # Yellow
            "START": "\033[94m",  # Blue
            "END": "\033[92m",  # Green
            "RESET": "\033[0m",
        },

        # 3. Cyber
        "cyber": {
            "WALL": "\033[35m",  # Magenta
            "PATH": "\033[96m",  # Cyan
            "START": "\033[94m",  # Blue
            "END": "\033[92m",  # Green
            "RESET": "\033[0m",
        },

        # 4. Classic Inverted
        "sketch": {
            "WALL": "\033[37m",  # Light G
            "PATH": "\033[90m",  # Gray
            "START": "\033[94m",  # Blue
            "END": "\033[92m",  # Green
            "RESET": "\033[0m",
        },

        # 5. Toxic/Radioactive
        "nuclear": {
            "WALL": "\033[32m",  # Green
            "PATH": "\033[95m",  # Pink
            "START": "\033[94m",  # Blue
            "END": "\033[92m",  # Green
            "RESET": "\033[0m",
        },
    }

    def __init__(self) -> None:
        """Initializes Graphics with default style (uni)
           and theme (midnight).
        """
        self._style_keys = tuple(self.SYMBOLS_STYLES.keys())
        self._theme_keys = tuple(self.COLORS_STYLES.keys())

        self._style_idx: int = 0
        self._theme_idx: int = 0

        self.show_path: bool = False

        self.current_style_name: str = self._style_keys[self._style_idx]
        self.current_theme_name: str = self._theme_keys[self._theme_idx]

        self.current_char_map = self.SYMBOLS_STYLES[self.current_style_name]
        self.current_theme_map = self.COLORS_STYLES[self.current_theme_name]

    def toggle_style(self) -> None:
        """Cycles to the next available symbol style
        (e.g., Unicode -> ASCII).
        """
        self._style_idx = (self._style_idx + 1) % len(self._style_keys)
        self.current_style_name = self._style_keys[self._style_idx]
        self.current_char_map = self.SYMBOLS_STYLES[
            self._style_keys[self._style_idx]]

    def toggle_theme(self) -> None:
        """Cycles to the next available color theme."""
        self._theme_idx = (self._theme_idx + 1) % len(self._theme_keys)
        self.current_theme_name = self._theme_keys[self._theme_idx]
        self.current_theme_map = self.COLORS_STYLES[
            self._theme_keys[self._theme_idx]]

    def get_char_for_cell(self, cell: Cell) -> str:
        """Determines the character representation for a cell
           based on connections.

        Creates a tuple mask (North, East, South, West) based on the cell's
        open paths and looks up the corresponding character in the current map.

        Args:
            cell (Cell): The cell object to render.

        Returns:
            str: The character representing the cell's walls/paths.
                 Returns '@' if the configuration is invalid.
        """
        mask = (
            cell.paths["north"],
            cell.paths["east"],
            cell.paths["south"],
            cell.paths["west"]
        )
        return self.current_char_map.get(mask, "@")

    def get_color_for_cell(self, cell: Cell) -> str:
        """Retrieves the ANSI color code for a cell based on its type.

        Prioritizes logic: Start > Exit > Solution Path (if enabled) > Wall.

        Args:
            cell (Cell): The cell object to color.

        Returns:
            str: An ANSI escape code string for the color.
        """
        theme = self.current_theme_map
        if cell.is_start:
            return theme["START"]

        if cell.is_exit:
            return theme["END"]

        if cell.is_solution and self.show_path:
            return theme["PATH"]

        if cell.forbidden:
            return theme["RESET"]

        return theme["WALL"]
