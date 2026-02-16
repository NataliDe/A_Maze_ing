"""
Renderer module.

Crisp maze rendering using a 2W+1 x 2H+1 grid.

Fix terminal aspect ratio:
- In UNI style we render each cell horizontally doubled to look more square:
  wall -> '██', empty -> '  ', solution -> '██', forbidden -> '▓▓'
- In ASCII style we keep single-width output to match
"Terminal ASCII rendering".

Colors:
- WALL, SOLUTION, FORBIDDEN, START, END, RESET
"""

from __future__ import annotations

import sys
from typing import Dict, List, Optional, Set, Tuple

from .cell import Cell
from .graphics import Graphics
from .grid import Grid
from .menu import Menu

Coord = Tuple[int, int]
CanvasPos = Tuple[int, int]  # (x, y)


class Renderer:
    """Terminal renderer for maze + menu using crisp grid style."""

    def __init__(self, grafix_module: Graphics, menu_module: Menu) -> None:
        self.gfx: Graphics = grafix_module
        self.menu: Menu = menu_module

    @staticmethod
    def clear_screen() -> None:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    @staticmethod
    def show_cursor() -> None:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def render_all(
        self,
        grid: Grid,
        is_path_visible: bool,
        solution: Optional[List[Cell]] = None,
        generator_name: str = "dfs",
    ) -> None:
        self.clear_screen()

        maze_lines = self._build_maze_lines(grid, is_path_visible, solution)
        sys.stdout.write("\n".join(maze_lines) + "\n")

        menu_list = [
            self.menu.get_title_text(),
            self.menu.get_generate_btn_text(),
            self.menu.get_path_btn_text(is_path_visible),
            self.menu.get_char_style_btn_text(self.gfx.current_style_name),
            self.menu.get_color_style_btn_text(self.gfx.current_theme_name),
            self.menu.get_generator_btn_text(generator_name),
            self.menu.get_exit_btn_text(),
            self.menu.get_choice(),
        ]
        sys.stdout.write("\n".join(menu_list))
        sys.stdout.flush()
        self.show_cursor()

    def _is_uni(self) -> bool:
        return self.gfx.current_style_name == "uni"

    # --- glyphs as single "cells" in the internal canvas ---
    def _wall_char(self) -> str:
        return "█" if self._is_uni() else "#"

    def _forbidden_char(self) -> str:
        return "♥" if self._is_uni() else "#"

    def _solution_char(self) -> str:
        return "░" if self._is_uni() else "."

    def _start_end_chars(self) -> Tuple[str, str]:
        # same char in UNI, colored by position
        return ("1", "2") if self._is_uni() else ("S", "F")

    def _empty_char(self) -> str:
        return " "

    # --- horizontal scaling ---
    def _px(self, ch: str) -> str:
        """
        Convert one canvas character into an output pixel string.

        UNI: double width (2 chars) for square look.
        ASCII: keep 1 char.
        """
        if not self._is_uni():
            return ch
        if ch == '2':
            return "▓▓"  # 🏆
        if ch == '1':
            return "▒▒"  # ▒🏓
        if ch == " ":
            return "  "
        return ch * 2

    def _build_maze_lines(
        self,
        grid: Grid,
        is_path_visible: bool,
        solution: Optional[List[Cell]],
    ) -> List[str]:
        w, h = grid.grid_width, grid.grid_height
        out_h = 2 * h + 1
        out_w = 2 * w + 1

        wall = self._wall_char()
        forb = self._forbidden_char()
        sol = self._solution_char()
        start_m, end_m = self._start_end_chars()
        empty = self._empty_char()

        canvas: List[List[str]] = [
            [wall for _ in range(out_w)] for _ in range(out_h)]
        forbidden_wall_positions: Set[Tuple[int, int]] = set()

        for y in range(h):
            for x in range(w):
                cell = grid[x, y]
                cx = 2 * x + 1
                cy = 2 * y + 1

                if cell.forbidden:
                    self._mark_forbidden_block(
                        forbidden_wall_positions,
                        cx=cx,
                        cy=cy,
                        max_x=out_w - 1,
                        max_y=out_h - 1,
                    )
                    continue

                canvas[cy][cx] = empty

                if cell.paths.get("north", True) is False:
                    canvas[cy - 1][cx] = empty
                if cell.paths.get("south", True) is False:
                    canvas[cy + 1][cx] = empty
                if cell.paths.get("west", True) is False:
                    canvas[cy][cx - 1] = empty
                if cell.paths.get("east", True) is False:
                    canvas[cy][cx + 1] = empty

        if is_path_visible and solution:
            self._draw_solution(canvas, solution, sol, empty)

        sx, sy = self._find_start(grid)
        ex, ey = self._find_exit(grid)

        start_pos: CanvasPos = (2 * sx + 1, 2 * sy + 1)
        end_pos: CanvasPos = (2 * ex + 1, 2 * ey + 1)

        canvas[start_pos[1]][start_pos[0]] = start_m
        canvas[end_pos[1]][end_pos[0]] = end_m

        return self._colorize_canvas(
            canvas=canvas,
            forbidden_wall_positions=forbidden_wall_positions,
            wall_char=wall,
            forbidden_char=forb,
            solution_char=sol,
            start_char=start_m,
            end_char=end_m,
            empty_char=empty,
            start_pos=start_pos,
            end_pos=end_pos,
        )

    @staticmethod
    def _mark_forbidden_block(
        pos: Set[Tuple[int, int]],
        cx: int,
        cy: int,
        max_x: int,
        max_y: int,
    ) -> None:
        for yy in range(cy - 1, cy + 2):
            if yy < 0 or yy > max_y:
                continue
            for xx in range(cx - 1, cx + 2):
                if xx < 0 or xx > max_x:
                    continue
                pos.add((yy, xx))

    def _draw_solution(
        self,
        canvas: List[List[str]],
        solution: List[Cell],
        sol_char: str,
        empty_char: str,
    ) -> None:
        if len(solution) < 2:
            return

        for i in range(len(solution) - 1):
            a = solution[i]
            b = solution[i + 1]

            ax = 2 * a.cell_x + 1
            ay = 2 * a.cell_y + 1
            bx = 2 * b.cell_x + 1
            by = 2 * b.cell_y + 1

            if canvas[ay][ax] == empty_char:
                canvas[ay][ax] = sol_char
            if canvas[by][bx] == empty_char:
                canvas[by][bx] = sol_char

            mx = (ax + bx) // 2
            my = (ay + by) // 2
            if canvas[my][mx] == empty_char:
                canvas[my][mx] = sol_char

    def _colorize_canvas(
        self,
        canvas: List[List[str]],
        forbidden_wall_positions: Set[Tuple[int, int]],
        wall_char: str,
        forbidden_char: str,
        solution_char: str,
        start_char: str,
        end_char: str,
        empty_char: str,
        start_pos: CanvasPos,
        end_pos: CanvasPos,
    ) -> List[str]:
        theme: Dict[str, str] = self.gfx.current_theme_map
        wall_c = theme["WALL"]
        sol_c = theme["SOLUTION"]
        forb_c = theme["FORBIDDEN"]
        start_c = theme["START"]
        end_c = theme["END"]
        reset = theme["RESET"]

        lines: List[str] = []
        for y, row in enumerate(canvas):
            out: List[str] = []
            for x, ch in enumerate(row):
                if ch == wall_char:
                    if (y, x) in forbidden_wall_positions:
                        out.append(
                            f"{forb_c}{self._px(forbidden_char)}{reset}")
                    else:
                        out.append(f"{wall_c}{self._px(wall_char)}{reset}")
                elif (x, y) == start_pos and ch == start_char:
                    out.append(f"{start_c}{self._px(start_char)}{reset}")
                elif (x, y) == end_pos and ch == end_char:
                    out.append(f"{end_c}{self._px(end_char)}{reset}")
                elif ch == solution_char:
                    out.append(f"{sol_c}{self._px(solution_char)}{reset}")
                elif ch == empty_char:
                    out.append(self._px(empty_char))
                else:
                    out.append(self._px(ch))
            lines.append("".join(out))
        return lines

    def _find_start(self, grid: Grid) -> Coord:
        for row in grid.matrix:
            for cell in row:
                if cell.is_start:
                    return (cell.cell_x, cell.cell_y)
        return (0, 0)

    def _find_exit(self, grid: Grid) -> Coord:
        for row in grid.matrix:
            for cell in row:
                if cell.is_exit:
                    return (cell.cell_x, cell.cell_y)
        return (grid.grid_width - 1, grid.grid_height - 1)
