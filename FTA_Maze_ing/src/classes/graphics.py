from .cell import Cell


class Graphics:
    SYMBOLS_STYLES = {
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

    COLORS_STYLES = {
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
        self._style_keys = tuple(self.SYMBOLS_STYLES.keys())
        self._theme_keys = tuple(self.COLORS_STYLES.keys())

        self._style_idx = 0
        self._theme_idx = 0

        self.show_path = False

        self.current_style_name = self._style_keys[self._style_idx]
        self.current_theme_name = self._theme_keys[self._theme_idx]

        self.current_char_map = self.SYMBOLS_STYLES[self.current_style_name]
        self.current_theme_map = self.COLORS_STYLES[self.current_theme_name]

    def toggle_style(self) -> None:
        self._style_idx = (self._style_idx + 1) % len(self._style_keys)
        self.current_style_name = self._style_keys[self._style_idx]
        self.current_char_map = self.SYMBOLS_STYLES[
            self._style_keys[self._style_idx]]

    def toggle_theme(self) -> None:
        self._theme_idx = (self._theme_idx + 1) % len(self._theme_keys)
        self.current_theme_name = self._theme_keys[self._theme_idx]
        self.current_theme_map = self.COLORS_STYLES[
            self._theme_keys[self._theme_idx]]

    def get_char_for_cell(self, cell: Cell) -> str:
        mask = (
            cell.paths["north"],
            cell.paths["east"],
            cell.paths["south"],
            cell.paths["west"]
        )
        return self.current_char_map.get(mask, "@")

    def get_color_for_cell(self, cell: Cell) -> str:
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
