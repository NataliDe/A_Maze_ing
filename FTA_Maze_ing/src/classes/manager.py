"""
The central controller for the A-Maze-Ing application.
"""

from __future__ import annotations

import sys
import time
from typing import Tuple, Union

# Note: These imports are based on the provided file content.
# Ensure these modules exist in your project structure.
from .builder import OriginShift
from .dfs_backtracker import DFSBacktracker
from .generators import GeneratorRegistry
from .grid import Grid
from .graphics import Graphics
from .kruskal_generator import KruskalGenerator
from .maze_config import MazeConfig
from .menu import Menu
from .mlx_viewer import MlxViewer
from .prim_generator import PrimGenerator
from .renderer import Renderer
from .solver import Solver
from .writer import MazeWriter

# Type aliases for clarity
Coord = Tuple[int, int]
Cmd = Union[int, str, None]


class Manager:
    """Application controller: coordinates generation, rendering, and IO.

    This class acts as the "brain" of the application (Controller pattern).
    It binds together the Data Model (Grid), the View (Renderer/Graphics),
    and the Business Logic (Generators/Solver). It handles the main event loop
    and processes user commands.

    Attributes:
        config (MazeConfig): Configuration settings.
        grid (Grid): The main maze grid object.
        gfx (Graphics): Visual style manager.
        menu (Menu): Menu text manager.
        renderer (Renderer): Terminal rendering engine.
        origin_shift (OriginShift): Specific builder instance for
        "Origin Shift" algo.
        registry (GeneratorRegistry): Manager for switching
        between algorithms.
        writer (MazeWriter): Handler for saving maze data to files.
        mlx_viewer (MlxViewer): Handler for external graphical window.
    """

    def __init__(self, config: MazeConfig) -> None:
        """Initializes the Manager and all core components.

        Args:
            config (MazeConfig): The configuration object loaded at startup.
        """
        self.config = config

        self.grid = Grid(config)
        self.gfx = Graphics()
        self.menu = Menu()
        self.renderer = Renderer(self.gfx, self.menu)

        # Special builder instance
        self.origin_shift = OriginShift(self.grid)

        # Initialize the strategy registry with available algorithms
        self.registry = GeneratorRegistry(
            generators={
                "origin_shift": self._origin_shift_adapter(),
                "dfs": DFSBacktracker(),
                "prim": PrimGenerator(),
                "kruskal": KruskalGenerator(),
            },
            order=("origin_shift", "dfs", "prim", "kruskal"),
        )

        self.writer = MazeWriter()
        self._last_path_dirs: str = ""

        self.mlx_viewer = MlxViewer()

    def run(self) -> None:
        """Starts the main application loop.

        Renders the initial state and enters an infinite loop waiting for
        user input. Dispatches commands to specific handler methods.
        """
        self.renderer.render_all(self.grid, self.registry.current().name)

        while True:
            try:
                command = self.menu.get_user_choice()
            except Exception:
                continue

            match command:
                case self.menu.CMD_EXIT:
                    self._handle_exit()

                case self.menu.CMD_GENERATE_NEW:
                    self._handle_generate()

                case self.menu.CMD_SHOW_PATH:
                    self._handle_toggle_path()

                case self.menu.CMD_CHAR_STYLE:
                    self.gfx.toggle_style()
                    self._rerender()

                case self.menu.CMD_CHANGE_COLORS:
                    self.gfx.toggle_theme()
                    self._rerender()

                case self.menu.CMD_CHANGE_GENERATOR:
                    self.registry.next()
                    self._rerender()

                case self.menu.CMD_OPEN_MLX:
                    self._handle_open_mlx()

                case _:
                    self._stub_action("Unknown command", command)

    # ---------------- actions ----------------

    def _handle_exit(self) -> None:
        """Handles the application exit sequence."""
        self._stub_action("Hasta la vista, baby.", self.menu.CMD_EXIT)
        self.renderer.clear_screen()
        sys.exit(0)

    def _handle_generate(self) -> None:
        """Orchestrates the maze generation workflow.

        Steps:
        1. Clears previous solution data.
        2. Invokes the currently selected generator.
        3. Solves the new maze to verify connectivity.
        4. Saves the maze data to a file.
        5. Re-renders the UI.

        Handles exceptions at each step and displays error
        messages via stub_action.
        """
        self._clear_solution_marks()
        self._last_path_dirs = ""

        gen = self.registry.current()
        try:
            gen.generate(self.grid, self._entry())
        except Exception as exc:
            self._stub_action(f"Generator failed: {exc}",
                              self.menu.CMD_GENERATE_NEW)
            return

        try:
            self._compute_solution()
        except Exception as exc:
            self._last_path_dirs = ""
            self._clear_solution_marks()
            self._stub_action(f"Solver failed: {exc}",
                              self.menu.CMD_GENERATE_NEW)

        try:
            self.writer.save(
                grid=self.grid,
                filename=self.config.output_file_name,
                entry=self._entry(),
                exit_=self._exit(),
                path_dirs=self._last_path_dirs,
            )
        except Exception as exc:
            self._stub_action(f"Save failed: {exc}",
                              self.menu.CMD_GENERATE_NEW)

        self._rerender()

    def _handle_toggle_path(self) -> None:
        """Toggles the visibility of the solution path.

        If the path has not been computed yet (or was lost), attempts to
        re-solve the maze before enabling visibility.
        """
        self.gfx.show_path = not self.gfx.show_path

        if self.gfx.show_path and not self._last_path_dirs:
            try:
                self._compute_solution()
            except Exception as exc:
                self._stub_action(f"Solver failed: {exc}",
                                  self.menu.CMD_SHOW_PATH)

        self._rerender()

    def _handle_open_mlx(self) -> None:
        """Launches the external MLX viewer.

        Reads the current maze state from the output file (maze.txt).
        Pauses the terminal UI while the window is open.
        """
        try:
            self.mlx_viewer.open_from_txt(self.config)
        except Exception as exc:
            self._stub_action(f"MLX failed: {exc}", self.menu.CMD_OPEN_MLX)
        finally:
            # after returning from MLX loop, redraw terminal UI
            self._rerender()

    # ---------------- solution ----------------

    def _compute_solution(self) -> None:
        """Solves the maze using the Solver module.

        Updates the grid cells with `is_solution` flags and stores the
        directional path string (e.g., "NNEES...") for saving.
        """
        self._clear_solution_marks()
        solver = Solver(self.grid)
        res = solver.solve(self._entry(), self._exit())
        self._last_path_dirs = res.path_dirs

        for (x, y) in res.path_coords:
            self.grid.matrix[y][x].is_solution = True

    def _clear_solution_marks(self) -> None:
        """Resets the solution flag for all cells in the grid."""
        for row in self.grid.matrix:
            for cell in row:
                cell.is_solution = False

    # ---------------- helpers ----------------

    def _rerender(self) -> None:
        """Triggers a full screen refresh via the Renderer."""
        self.renderer.render_all(self.grid, self.registry.current().name)

    def _entry(self) -> Coord:
        """Returns the start coordinates (x, y) from config."""
        x, y = self.config.maze_entry
        return (x, y)

    def _exit(self) -> Coord:
        """Returns the exit coordinates (x, y) from config."""
        x, y = self.config.maze_exit
        return (x, y)

    def _origin_shift_adapter(self):
        """Creates an adapter for the OriginShift builder to
        match the Generator interface.

        Returns:
            Any: An object with a `generate(grid, start)` method.
        """
        manager = self

        class _OriginShiftGen:
            name = "origin_shift"

            def generate(self, grid: Grid, start: Coord) -> None:
                manager.origin_shift.init_vectors()
                total = grid.grid_width * grid.grid_height
                iterations = total * 10
                for _ in range(iterations):
                    manager.origin_shift.step()

        return _OriginShiftGen()

    def _stub_action(self, message: str, command: Cmd) -> None:
        """Displays a temporary status message and cleans the input line.

        Used to show errors or confirmations without breaking the UI layout.

        Args:
            message (str): The text to display.
            command (Cmd): The command that triggered the action
            (used for cursor calc).
        """
        cmd_len = 1 if isinstance(command, int) else len(str(command))
        msg_y = self.grid.grid_height + len(self.menu.menu_list) + 2
        full = f">>> {message}"

        self.renderer.move_cursor(1, msg_y)
        sys.stdout.write("\033[K")
        self.renderer.type_text(full, 0.0, 0.0)
        sys.stdout.flush()

        time.sleep(2)

        self.renderer.backspace(len(full), 0.0, 0.0)
        outset = len(self.menu.get_choice()) + 1 + cmd_len
        self.renderer.move_cursor(outset, msg_y - 1)
        self.renderer.backspace(cmd_len, 0.0, 0.0)
        sys.stdout.flush()
