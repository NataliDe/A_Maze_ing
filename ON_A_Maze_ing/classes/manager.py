"""
Manager module.

Coordinates config, grid, generators, solver, rendering, and file output.
Adds a center obstacle shaped as "42" using forbidden cells.
The "42" mask auto-scales depending on maze size (safe for small mazes).
"""

from __future__ import annotations

import sys
import time
from typing import List, Tuple

from .cell import Cell
from .generator import MazeGenerator
from .generators import DFSBacktrackerGenerator
from .generators import OriginShiftGenerator, PrimGenerator
from .graphics import Graphics
from .grid import Grid
from .maze_config import MazeConfig
from .menu import Menu
from .renderer import Renderer
from .solver import Solver
from .writer import MazeWriter

Coord = Tuple[int, int]


class Manager:
    """Main application manager: UI loop + maze logic."""

    def __init__(self, config: MazeConfig) -> None:
        self.config: MazeConfig = config

        self.grid: Grid = Grid(config.maze_width, config.maze_height)
        self.gfx: Graphics = Graphics()
        self.menu: Menu = Menu()
        self.renderer: Renderer = Renderer(self.gfx, self.menu)

        self.writer: MazeWriter = MazeWriter()

        self.is_path_visible: bool = False
        self.solution: List[Cell] = []
        self.last_path_dirs: str = ""

        self._generators: List[Tuple[str, MazeGenerator]] = [
            ("dfs", DFSBacktrackerGenerator()),
            ("prim", PrimGenerator()),
            ("origin-shift", OriginShiftGenerator(iterations_multiplier=10)),
        ]
        self._gen_idx: int = 0

        self._apply_entry_exit_flags()
        self._apply_forbidden_42()
        self._generate_maze()

    @property
    def generator_name(self) -> str:
        return self._generators[self._gen_idx][0]

    @property
    def generator(self) -> MazeGenerator:
        return self._generators[self._gen_idx][1]

    def run(self) -> None:
        self._render()

        while True:
            try:
                command = self.menu.get_user_choice()
            except (EOFError, KeyboardInterrupt):
                self.renderer.clear_screen()
                print("[SYSTEM]: Bye.")
                return

            if command == self.menu.CMD_EXIT:
                self.renderer.clear_screen()
                print("[SYSTEM]: Hasta la vista, baby.")
                return

            if command == self.menu.CMD_GENERATE_NEW:
                self._safe_generate_and_render()
                continue

            if command == self.menu.CMD_SHOW_PATH:
                self._safe_toggle_path_and_render()
                continue

            if command == self.menu.CMD_CHAR_STYLE:
                self.gfx.toggle_style()
                self._render()
                continue

            if command == self.menu.CMD_CHANGE_COLORS:
                self.gfx.toggle_theme()
                self._render()
                continue

            if command == self.menu.CMD_CHANGE_GENERATOR:
                self._gen_idx = (self._gen_idx + 1) % len(self._generators)
                self._safe_generate_and_render()
                continue

            self._stub_message("Unknown command")

    def _render(self) -> None:
        self.renderer.render_all(
            self.grid,
            self.is_path_visible,
            self.solution,
            generator_name=self.generator_name,
        )

    def _safe_generate_and_render(self) -> None:
        try:
            self._generate_maze()
            self.solution = []
            self.last_path_dirs = ""
            self.is_path_visible = False
        except Exception as exc:
            self._stub_message(f"Generate failed: {exc}")
        self._render()

    def _safe_toggle_path_and_render(self) -> None:
        self.is_path_visible = not self.is_path_visible

        if self.is_path_visible:
            try:
                self.solution = self._solve_maze()
                if not self.solution:
                    self._stub_message("Path not found")
            except Exception as exc:
                self.solution = []
                self.last_path_dirs = ""
                self._stub_message(f"Solve failed: {exc}")
        else:
            self.solution = []
            self.last_path_dirs = ""

        self._render()

    def _entry_coord(self) -> Coord:
        return (int(self.config.maze_entry[0]), int(self.config.maze_entry[1]))

    def _exit_coord(self) -> Coord:
        return (int(self.config.maze_exit[0]), int(self.config.maze_exit[1]))

    def _apply_entry_exit_flags(self) -> None:
        sx, sy = self._entry_coord()
        ex, ey = self._exit_coord()

        for row in self.grid.matrix:
            for cell in row:
                cell.is_start = False
                cell.is_exit = False

        self.grid[sx, sy].is_start = True
        self.grid[ex, ey].is_exit = True

        # Ensure start/end are never forbidden
        self.grid[sx, sy].forbidden = False
        self.grid[ex, ey].forbidden = False

    def _apply_forbidden_42(self) -> None:
        """
        Mark center cells as forbidden to form digits "4" and "2".

        Auto-scale:
        - Prefer big font 7x5 if maze fits
        - Otherwise use small font 5x3 if maze fits
        - Otherwise do nothing (no crash)
        """
        big_4 = [
            "10010",
            "10010",
            "10010",
            "11111",
            "00010",
            "00010",
            "00010",
        ]
        big_2 = [
            "11111",
            "00001",
            "00001",
            "11111",
            "10000",
            "10000",
            "11111",
        ]

        small_4 = [
            "101",
            "101",
            "111",
            "001",
            "001",
        ]
        small_2 = [
            "111",
            "001",
            "111",
            "100",
            "111",
        ]

        gap = 1

        chosen_4: List[str]
        chosen_2: List[str]

        # try big
        if self._mask_fits(big_4, big_2, gap):
            chosen_4 = big_4
            chosen_2 = big_2
        elif self._mask_fits(small_4, small_2, gap):
            chosen_4 = small_4
            chosen_2 = small_2
        else:
            return

        start_x, start_y = self._centered_origin(chosen_4, chosen_2, gap)

        self._apply_digit_mask(chosen_4, start_x, start_y)
        off_x = start_x + len(chosen_4[0]) + gap
        self._apply_digit_mask(chosen_2, off_x, start_y)

        # Ensure entry/exit are not forbidden
        self._apply_entry_exit_flags()

    def _mask_fits(self, d4: List[str], d2: List[str], gap: int) -> bool:
        digit_h = len(d4)
        digit_w = len(d4[0])
        total_w = digit_w + gap + len(d2[0])
        total_h = digit_h

        return (
            self.grid.grid_width >= total_w + 2
            and self.grid.grid_height >= total_h + 2
        )

    def _centered_origin(
            self, d4: List[str], d2: List[str], gap: int) -> Tuple[int, int]:
        digit_h = len(d4)
        total_w = len(d4[0]) + gap + len(d2[0])

        start_x = (self.grid.grid_width - total_w) // 2
        start_y = (self.grid.grid_height - digit_h) // 2
        return start_x, start_y

    def _apply_digit_mask(
            self, mask: List[str], origin_x: int, origin_y: int) -> None:
        for ry, row in enumerate(mask):
            for rx, ch in enumerate(row):
                if ch != "1":
                    continue
                x = origin_x + rx
                y = origin_y + ry
                if (
                    0 <= x < self.grid.grid_width
                    and 0 <= y < self.grid.grid_height
                ):
                    self.grid[x, y].forbidden = True

    def _generate_maze(self) -> None:
        """
        Generate the maze and write it to output file.

        IMPORTANT:
        - We always compute a valid path string for output file
        (Moulinette-friendly),
        even if UI path visibility is OFF.
        """
        entry = self._entry_coord()
        exit_ = self._exit_coord()

        self.generator.generate(self.grid, start=entry)

        self._apply_entry_exit_flags()
        self._apply_forbidden_42()

        # Always compute path for output file
        try:
            solver = Solver(self.grid)
            result = solver.solve(entry, exit_)
            self.last_path_dirs = result.path_dirs
            # keep UI hidden unless user asked
            if self.is_path_visible:
                self.solution = result.path_cells
            else:
                self.solution = []
        except Exception:
            # fallback: still save maze, but empty path
            self.last_path_dirs = ""
            self.solution = []

        self._safe_write_output(entry, exit_, self.last_path_dirs)

    def _solve_maze(self) -> List[Cell]:
        entry = self._entry_coord()
        exit_ = self._exit_coord()

        solver = Solver(self.grid)
        result = solver.solve(entry, exit_)

        self.last_path_dirs = result.path_dirs
        self._safe_write_output(entry, exit_, self.last_path_dirs)

        return result.path_cells

    def _safe_write_output(
            self, entry: Coord, exit_: Coord, path_dirs: str) -> None:
        try:
            self.writer.save(
                self.grid,
                self.config.output_file_name,
                entry=entry,
                exit_=exit_,
                path_dirs=path_dirs,
            )
        except OSError as exc:
            self._stub_message(f"Write failed: {exc}")

    def _stub_message(self, message: str) -> None:
        text = f">>> {message}"

        # place message below the maze+menu, safe-ish even for small mazes
        msg_y = (2 * self.grid.grid_height + 1) + 10

        sys.stdout.write(f"\033[{msg_y};1H")
        sys.stdout.write("\033[K")
        sys.stdout.write(text)
        sys.stdout.flush()

        time.sleep(2)

        sys.stdout.write(f"\033[{msg_y};1H")
        sys.stdout.write("\033[K")
        sys.stdout.flush()
