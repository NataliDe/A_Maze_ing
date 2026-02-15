"""
Renderer module.

Crisp maze rendering using a 2W+1 x 2H+1 grid.

Style:
- ascii:
    walls '#', start 'S', finish 'F', solution '.'
- uni:
    walls '█',
    start/finish SAME char '■' but different colors,
    solution also '■' with SOLUTION color.

Colors (from theme):
- WALL
- SOLUTION
- FORBIDDEN
- START
- END
- RESET

Forbidden ("42") is rendered as solid 3x3 blocks and colored FORBIDDEN.
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

    EMPTY_CHAR: str = " "

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

    def _wall_char(self) -> str:
        return "█" if self._is_uni() else "#"

    def _start_end_markers(self) -> Tuple[str, str]:
        if self._is_uni():
            return ("■", "■")  # same marker, colored by position
        return ("S", "F")

    def _solution_marker(self) -> str:
        return "⋄" if self._is_uni() else "."

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
        start_m, end_m = self._start_end_markers()
        sol_m = self._solution_marker()

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

                canvas[cy][cx] = self.EMPTY_CHAR

                if cell.paths.get("north", True) is False:
                    canvas[cy - 1][cx] = self.EMPTY_CHAR
                if cell.paths.get("south", True) is False:
                    canvas[cy + 1][cx] = self.EMPTY_CHAR
                if cell.paths.get("west", True) is False:
                    canvas[cy][cx - 1] = self.EMPTY_CHAR
                if cell.paths.get("east", True) is False:
                    canvas[cy][cx + 1] = self.EMPTY_CHAR

        if is_path_visible and solution:
            self._draw_solution(canvas, solution, sol_m)

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
            solution_marker=sol_m,
            start_marker=start_m,
            end_marker=end_m,
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
        """Mark a solid 3x3 block centered at (cx, cy) as forbidden."""
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
        solution_marker: str,
    ) -> None:
        """Mark solution cells and connectors with solution_marker."""
        if len(solution) < 2:
            return

        for i in range(len(solution) - 1):
            a = solution[i]
            b = solution[i + 1]

            ax = 2 * a.cell_x + 1
            ay = 2 * a.cell_y + 1
            bx = 2 * b.cell_x + 1
            by = 2 * b.cell_y + 1

            if canvas[ay][ax] == self.EMPTY_CHAR:
                canvas[ay][ax] = solution_marker
            if canvas[by][bx] == self.EMPTY_CHAR:
                canvas[by][bx] = solution_marker

            mx = (ax + bx) // 2
            my = (ay + by) // 2
            if canvas[my][mx] == self.EMPTY_CHAR:
                canvas[my][mx] = solution_marker

    def _colorize_canvas(
        self,
        canvas: List[List[str]],
        forbidden_wall_positions: Set[Tuple[int, int]],
        wall_char: str,
        solution_marker: str,
        start_marker: str,
        end_marker: str,
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
                        out.append(f"{forb_c}{ch}{reset}")
                    else:
                        out.append(f"{wall_c}{ch}{reset}")
                elif (x, y) == start_pos and ch == start_marker:
                    out.append(f"{start_c}{ch}{reset}")
                elif (x, y) == end_pos and ch == end_marker:
                    out.append(f"{end_c}{ch}{reset}")
                elif ch == solution_marker:
                    out.append(f"{sol_c}{ch}{reset}")
                else:
                    out.append(ch)
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
