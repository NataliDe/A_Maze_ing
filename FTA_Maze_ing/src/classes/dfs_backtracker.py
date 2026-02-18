"""
dfs_backtracker.py

Perfect maze generator: DFS recursive backtracker.
Open passages by setting cell.paths[dir] = True on both cells.
"""

import random
from typing import List, Tuple

from .grid import Grid

Coord = Tuple[int, int]


class DFSBacktracker:
    """DFS recursive backtracker generator."""

    name = "dfs"

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
        """Generate perfect maze with DFS."""
        self._reset_grid(grid)

        sx, sy = start
        stack: List[Coord] = [(sx, sy)]
        grid.matrix[sy][sx].visited = True

        while stack:
            x, y = stack[-1]
            neighbors = self._unvisited_neighbors(grid, x, y)
            if not neighbors:
                stack.pop()
                continue

            nx, ny, direction = random.choice(neighbors)
            self._carve(grid, x, y, nx, ny, direction)
            grid.matrix[ny][nx].visited = True
            stack.append((nx, ny))

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

    def _unvisited_neighbors(self, grid: Grid, x: int, y: int) -> List[Tuple[int, int, str]]:
        out: List[Tuple[int, int, str]] = []
        for d, (dx, dy) in self._DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < grid.grid_width and 0 <= ny < grid.grid_height):
                continue
            ncell = grid.matrix[ny][nx]
            if ncell.forbidden or ncell.visited:
                continue
            out.append((nx, ny, d))
        return out

    def _carve(self, grid: Grid, x: int, y: int, nx: int, ny: int, d: str) -> None:
        cell = grid.matrix[y][x]
        ncell = grid.matrix[ny][nx]
        cell.paths[d] = True
        ncell.paths[self._OPPOSITE[d]] = True
