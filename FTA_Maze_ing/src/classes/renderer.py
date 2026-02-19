"""
Handles all terminal output and visual rendering logic.
"""

import random
import sys
import time

from .cell import Cell
from .graphics import Graphics
from .grid import Grid
from .menu import Menu


class Renderer:
    """Orchestrates the visualization of the maze and UI components.

    This class serves as an abstraction layer for terminal manipulation.
    It handles cursor movement, screen clearing, text typing effects, and
    delegates specific character/color choices to the Graphics module.

    Attributes:
        gfx (Graphics): Reference to the graphics module for style/theme data.
        menu (Menu): Reference to the menu module for UI text generation.
    """
    def __init__(self, grafix_module: Graphics, menu_module: Menu) -> None:
        """Initializes the Renderer.

        Args:
            grafix_module (Graphics): Instance handling visual styles.
            menu_module (Menu): Instance handling menu text logic.
        """
        self.gfx = grafix_module
        self.menu = menu_module

    @staticmethod
    def clear_screen() -> None:
        """Clears the entire terminal screen and moves cursor to home (0,0).

        Uses ANSI escape codes: \033[2J (clear entire screen)
        and \033[H (home).
        """
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    @staticmethod
    def hide_cursor() -> None:
        """Hides the terminal cursor to prevent flickering during rendering.
        """
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

    @staticmethod
    def show_cursor() -> None:
        """Restores the terminal cursor visibility."""
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    @staticmethod
    def save_cursor() -> None:
        """Saves the current cursor position in the terminal memory."""
        sys.stdout.write("\0337")
        sys.stdout.flush()

    @staticmethod
    def restore_cursor() -> None:
        """Restores the cursor to the previously saved position."""
        sys.stdout.write("\0338")
        sys.stdout.flush()

    @staticmethod
    def move_cursor(x: int, y: int) -> None:
        """Moves the cursor to specific coordinates.

        Args:
            x (int): Column number (1-based index).
            y (int): Row number (1-based index).
        """
        sys.stdout.write(f"\033[{y};{x}H")

    @staticmethod
    def type_text(text: str, min_delay: float = 0.04,
                  max_delay: float = 0.09) -> None:
        """Prints text character by character to simulate typing.

        Args:
            text (str): The string to display.
            min_delay (float): Minimum sleep time between chars.
            max_delay (float): Maximum sleep time between chars.
        """
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(random.uniform(min_delay, max_delay))

    @staticmethod
    def backspace(count: int, min_delay: float = 0.04,
                  max_delay: float = 0.09) -> None:
        """Simulates pressing backspace to erase characters.

        Args:
            count (int): Number of characters to erase.
            min_delay (float): Minimum sleep time between backspaces.
            max_delay (float): Maximum sleep time between backspaces.
        """
        for _ in range(count):
            sys.stdout.write("\b \b")
            sys.stdout.flush()
            time.sleep(random.uniform(min_delay, max_delay))

    def draw_cell(self, cell: Cell, delay: float = 0.02) -> None:
        """Renders a single cell at its calculated screen position.

        Retrieves the appropriate character and color from the Graphics module
        and prints it at the specific (x, y) coordinate.

        Args:
            cell (Cell): The cell object to draw.
            delay (float): Optional pause after drawing
            (for animation effects).
        """
        # Convert 0-based grid coordinates to 1-based terminal coordinates
        screen_y = cell.cell_y + 1
        screen_x = cell.cell_x + 1

        char = self.gfx.get_char_for_cell(cell)
        color = self.gfx.get_color_for_cell(cell)
        reset = self.gfx.current_theme_map["RESET"]

        self.move_cursor(screen_x, screen_y)
        sys.stdout.write(f"{color}{char}{reset}")
        sys.stdout.flush()
        time.sleep(delay)

    def redraw_grid(self, grid: Grid) -> None:
        """Refreshes the entire maze grid visualization.

        Iterates through the entire matrix and redraws every cell.
        Hides the cursor during the process to minimize visual noise.

        Args:
            grid (Grid): The grid object containing the cells.
        """
        self.hide_cursor()
        for row in grid.matrix:
            for cell in row:
                self.draw_cell(cell, 0)
        self.show_cursor()

    def update_menu_line(self, grid: Grid,
                         gen_name: str, line_index: int) -> None:
        """Updates a specific line in the menu section below the maze.

        Args:
            grid (Grid): Used to calculate the Y-offset (below the maze).
            gen_name (str): Name of the current generation algorithm
            (for display).
            line_index (int): The index of the menu line to update.
        """
        current_y = grid.grid_height + 2 + line_index

        menu_list = self.menu.get_current_list(
            path_visible=self.gfx.show_path,
            char_style=self.gfx.current_style_name,
            color_style=self.gfx.current_theme_name,
            gen_name=gen_name,
        )
        text = menu_list[line_index]

        self.move_cursor(1, current_y)
        sys.stdout.write("\033[K")
        self.type_text(text)
        sys.stdout.flush()

    def render_all(self, grid: Grid, gen_name: str) -> None:
        """Performs a full render of the application interface.

        Clears the screen, draws the maze grid, and renders the menu options.

        Args:
            grid (Grid): The maze grid to render.
            gen_name (str): The name of the algorithm to display in the UI.
        """
        self.clear_screen()

        menu_list = self.menu.get_current_list(
            path_visible=self.gfx.show_path,
            char_style=self.gfx.current_style_name,
            color_style=self.gfx.current_theme_name,
            gen_name=gen_name,
        )

        # Draw Grid
        for row in grid.matrix:
            for cell in row:
                self.draw_cell(cell)

        # Spacer
        self.move_cursor(1, grid.grid_height + 1)
        print(" " * grid.grid_width)

        # Draw Menu
        for i in range(len(menu_list)):
            self.update_menu_line(grid, gen_name, i)

        self.show_cursor()
