"""
Graphics module.

Provides:
- symbol styles (kept for compatibility)
- color themes (ANSI codes)

Theme keys used by renderer:
- WALL, SOLUTION, FORBIDDEN, START, END, RESET
We also keep PATH as an alias of SOLUTION for backward compatibility.
"""

from __future__ import annotations

from typing import Dict, Tuple


class Graphics:
    """Holds rendering styles and color themes."""

    SYMBOLS_STYLES: Dict[str, Dict[Tuple[bool, bool, bool, bool], str]] = {
        "uni": {},
        "ascii": {},
    }

    COLORS_STYLES: Dict[str, Dict[str, str]] = {
        "midnight": {
            "WALL": "\033[90m",       # gray
            "SOLUTION": "\033[96m",   # cyan
            "PATH": "\033[96m",       # alias
            "FORBIDDEN": "\033[95m",  # magenta
            "START": "\033[94m",      # blue
            "END": "\033[92m",        # green
            "RESET": "\033[0m",
        },
        "sunset": {
            "WALL": "\033[31m",       # red
            "SOLUTION": "\033[93m",   # yellow
            "PATH": "\033[93m",       # alias
            "FORBIDDEN": "\033[35m",  # magenta
            "START": "\033[94m",      # blue
            "END": "\033[92m",        # green
            "RESET": "\033[0m",
        },
        "cyber": {
            "WALL": "\033[35m",       # magenta
            "SOLUTION": "\033[96m",   # cyan
            "PATH": "\033[96m",       # alias
            "FORBIDDEN": "\033[91m",  # bright red
            "START": "\033[92m",      # green
            "END": "\033[93m",        # yellow
            "RESET": "\033[0m",
        },
        "sketch": {
            "WALL": "\033[37m",       # light gray
            "SOLUTION": "\033[90m",   # dark gray
            "PATH": "\033[90m",       # alias
            "FORBIDDEN": "\033[91m",  # bright red
            "START": "\033[94m",      # blue
            "END": "\033[92m",        # green
            "RESET": "\033[0m",
        },
        "nuclear": {
            "WALL": "\033[32m",       # green
            "SOLUTION": "\033[95m",   # pink/magenta
            "PATH": "\033[95m",       # alias
            "FORBIDDEN": "\033[93m",  # yellow
            "START": "\033[96m",      # cyan
            "END": "\033[91m",        # bright red
            "RESET": "\033[0m",
        },
    }

    def __init__(self) -> None:
        self._style_keys = tuple(self.SYMBOLS_STYLES.keys())
        self._theme_keys = tuple(self.COLORS_STYLES.keys())

        self._style_idx = self._style_keys.index("ascii")
        self._theme_idx = 0

        self.current_style_name = self._style_keys[self._style_idx]
        self.current_theme_name = self._theme_keys[self._theme_idx]

        self.current_char_map = self.SYMBOLS_STYLES[self.current_style_name]
        self.current_theme_map = self.COLORS_STYLES[self.current_theme_name]

    def toggle_style(self) -> None:
        """Cycle between available symbol styles."""
        self._style_idx = (self._style_idx + 1) % len(self._style_keys)
        self.current_style_name = self._style_keys[self._style_idx]
        self.current_char_map = self.SYMBOLS_STYLES[self.current_style_name]

    def toggle_theme(self) -> None:
        """Cycle between available color themes."""
        self._theme_idx = (self._theme_idx + 1) % len(self._theme_keys)
        self.current_theme_name = self._theme_keys[self._theme_idx]
        self.current_theme_map = self.COLORS_STYLES[self.current_theme_name]
