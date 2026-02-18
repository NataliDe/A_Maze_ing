"""
prim_generator.py

Randomized Prim's algorithm generator.
"""


import random
from typing import List, Tuple

from .grid import Grid

Coord = Tuple[int, int]


class PrimGenerator:
    """Randomized Prim generator."""

    name = "prim"

    _DIRS = {
        "north": (0, -1),
        "east": (1, 0),
        "south": (0, 1),
        "west": (-1, 0),
    }

    _OPPOSITE = {
        "north": "south",
        "south": "north",
        "east": "west",
        "west": "east",
    }

    def generate(self, grid: Grid, start: Coord) -> None:
        self._reset_grid(grid)

        sx, sy = start
        grid.matrix[sy][sx].visited = True

        frontier: List[Tuple[int, int, int, int, str]] = []
        self._add_frontier(grid, sx, sy, frontier)

        while frontier:
            x, y, px, py, d = frontier.pop(random.randrange(len(frontier)))
            cell = grid.matrix[y][x]
            if cell.forbidden or cell.visited:
                continue

            # connect cell to parent
            self._carve(grid, px, py, x, y, d)
            cell.visited = True
            self._add_frontier(grid, x, y, frontier)

    def _reset_grid(self, grid: Grid) -> None:
        for row in grid.matrix:
            for cell in row:
                if cell.forbidden:
                    continue
                cell.visited = False
                cell.is_solution = False
                cell.vector = None
                for k in cell.paths:
                    cell.paths[k] = False

    def _add_frontier(
        self,
        grid: Grid,
        x: int,
        y: int,
        frontier: List[Tuple[int, int, int, int, str]],
    ) -> None:
        for d, (dx, dy) in self._DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < grid.grid_width and 0 <= ny < grid.grid_height):
                continue
            ncell = grid.matrix[ny][nx]
            if ncell.forbidden or ncell.visited:
                continue
            frontier.append((nx, ny, x, y, d))

    def _carve(self, grid: Grid, x: int, y: int, nx: int, ny: int, d: str) -> None:
        cell = grid.matrix[y][x]
        ncell = grid.matrix[ny][nx]
        cell.paths[d] = True
        ncell.paths[self._OPPOSITE[d]] = True
