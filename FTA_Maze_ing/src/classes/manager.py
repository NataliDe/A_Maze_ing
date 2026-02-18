from __future__ import annotations

import sys
import time
from typing import Tuple, Union

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

Coord = Tuple[int, int]
Cmd = Union[int, str, None]


class Manager:
    """Application controller: generate, solve, render, save, MLX view."""

    def __init__(self, config: MazeConfig) -> None:
        self.config = config

        self.grid = Grid(config)
        self.gfx = Graphics()
        self.menu = Menu()
        self.renderer = Renderer(self.gfx, self.menu)

        self.origin_shift = OriginShift(self.grid)

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

        # self.mlx_viewer = MlxViewer()

    def run(self) -> None:
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
        self._stub_action("Hasta la vista, baby.", self.menu.CMD_EXIT)
        self.renderer.clear_screen()
        sys.exit(0)

    def _handle_generate(self) -> None:
        self._clear_solution_marks()
        self._last_path_dirs = ""

        gen = self.registry.current()
        try:
            gen.generate(self.grid, self._entry())
        except Exception as exc:
            self._stub_action(f"Generator failed: {exc}", self.menu.CMD_GENERATE_NEW)
            return

        try:
            self._compute_solution()
        except Exception as exc:
            self._last_path_dirs = ""
            self._clear_solution_marks()
            self._stub_action(f"Solver failed: {exc}", self.menu.CMD_GENERATE_NEW)

        try:
            self.writer.save(
                grid=self.grid,
                filename=self.config.output_file_name,
                entry=self._entry(),
                exit_=self._exit(),
                path_dirs=self._last_path_dirs,
            )
        except Exception as exc:
            self._stub_action(f"Save failed: {exc}", self.menu.CMD_GENERATE_NEW)

        self._rerender()

    def _handle_toggle_path(self) -> None:
        self.gfx.show_path = not self.gfx.show_path

        if self.gfx.show_path and not self._last_path_dirs:
            try:
                self._compute_solution()
            except Exception as exc:
                self._stub_action(f"Solver failed: {exc}", self.menu.CMD_SHOW_PATH)

        self._rerender()

    def _handle_open_mlx(self) -> None:
        try:
            viewer = MlxViewer()
            viewer.open_from_txt(self.config)
        except Exception as exc:
            self._stub_action(f"MLX failed: {exc}", self.menu.CMD_OPEN_MLX)
        finally:
            self._rerender()


    # ---------------- solution ----------------

    def _compute_solution(self) -> None:
        self._clear_solution_marks()
        solver = Solver(self.grid)
        res = solver.solve(self._entry(), self._exit())
        self._last_path_dirs = res.path_dirs

        for (x, y) in res.path_coords:
            self.grid.matrix[y][x].is_solution = True

    def _clear_solution_marks(self) -> None:
        for row in self.grid.matrix:
            for cell in row:
                cell.is_solution = False

    # ---------------- helpers ----------------

    def _rerender(self) -> None:
        self.renderer.render_all(self.grid, self.registry.current().name)

    def _entry(self) -> Coord:
        x, y = self.config.maze_entry
        return (x, y)

    def _exit(self) -> Coord:
        x, y = self.config.maze_exit
        return (x, y)

    def _origin_shift_adapter(self):
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
