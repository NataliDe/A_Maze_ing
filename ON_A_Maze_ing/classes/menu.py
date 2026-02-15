"""
Menu module.

Provides command IDs and user input parsing for the CLI UI.
"""

from __future__ import annotations


class Menu:
    """
    Text menu for interacting with the maze program.
    """

    CMD_GENERATE_NEW: int = 1
    CMD_SHOW_PATH: int = 2
    CMD_CHAR_STYLE: int = 3
    CMD_CHANGE_COLORS: int = 4
    CMD_CHANGE_GENERATOR: int = 5
    CMD_EXIT: int = 6

    def __init__(self) -> None:
        """Initialize menu constants and title."""
        self.title: str = "=== A-MAZE-ING GENERATOR ==="

    def get_user_choice(self) -> int | str:
        """
        Read a command from user.

        Returns:
            If user enters a number within valid range -> int command.
            Otherwise -> raw string command (for future extensions).
        """
        choice = input("").strip()

        if choice.isdigit():
            cmd = int(choice)
            if 1 <= cmd <= self.CMD_EXIT:
                return cmd

        return choice

    def get_choice(self) -> str:
        """
        Prompt text for command input line.

        Returns:
            Prompt string.
        """
        return "Choose command: "

    def get_title_text(self) -> str:
        """Return menu title line."""
        return self.title

    def get_generate_btn_text(self) -> str:
        """Return text for 'generate new maze' command."""
        return f"[{self.CMD_GENERATE_NEW}] Generate new maze"

    def get_path_btn_text(self, is_path_visible: bool = False) -> str:
        """
        Return text for 'show/hide path' command.

        Args:
            is_path_visible: Current path visibility state.

        Returns:
            Menu line.
        """
        action = "Hide" if is_path_visible else "Show"
        return f"[{self.CMD_SHOW_PATH}] {action} path"

    def get_char_style_btn_text(self, char_style: str) -> str:
        """
        Return text for 'change character style' command.

        Args:
            char_style: Current character style name.

        Returns:
            Menu line.
        """
        return (
            f"[{self.CMD_CHAR_STYLE}] "
            f"Change characters style. Now: ({char_style})"
        )

    def get_color_style_btn_text(self, color_style: str) -> str:
        """
        Return text for 'change color theme' command.

        Args:
            color_style: Current theme name.

        Returns:
            Menu line.
        """
        return (
            f"[{self.CMD_CHANGE_COLORS}] "
            f"Change color style. Now: ({color_style})"
        )

    def get_generator_btn_text(self, generator_name: str) -> str:
        """
        Return text for 'change generator' command.

        Args:
            generator_name: Active generator name.

        Returns:
            Menu line.
        """
        return (
            f"[{self.CMD_CHANGE_GENERATOR}] "
            f"Change generator. Now: ({generator_name})"
        )

    def get_exit_btn_text(self) -> str:
        """Return text for 'exit' command."""
        return f"[{self.CMD_EXIT}] Quit program"
