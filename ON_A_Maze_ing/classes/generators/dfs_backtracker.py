"""
DFS backtracker generator.

Creates a perfect maze using iterative depth-first search with a stack.
Skips forbidden cells (they remain solid obstacles).
"""

from __future__ import annotations

import random
from typing import Dict, List, Tuple

from ..cell import Cell
from ..generator import Coord, MazeGenerator
from ..grid import Grid


class DFSBacktrackerGenerator(MazeGenerator):
    """
    Perfect maze generator (DFS / recursive backtracker), skipping forbidden cells.

    Convention used:
        cell.paths[dir] == True  -> wall CLOSED
        cell.paths[dir] == False -> passage OPEN
    """

    DIRS: Dict[str, Coord] = {
        "north": (0, -1),
        "east": (1, 0),
        "south": (0, 1),
        "west": (-1, 0),
    }

    OPPOSITE: Dict[str, str] = {
        "north": "south",
        "east": "west",
        "south": "north",
        "west": "east",
    }

    def generate(self, grid: Grid, start: Coord | None = None) -> None:
        """
        Generate a maze in-place. Forbidden cells are never visited/carved.

        Args:
            grid: Grid to modify.
            start: Optional start coordinate (x, y). Defaults to first non-forbidden.

        Returns:
            None.
        """
        self._reset_grid(grid)

        if start is None:
            start = self._first_free_cell(grid)

        sx, sy = start
        if grid[sx, sy].forbidden:
            start = self._first_free_cell(grid)
            sx, sy = start

        # Standard DFS for one connected component reachable from start,
        # but we ensure every non-forbidden cell gets visited by restarting.
        self._dfs_from(grid, (sx, sy))

        # If there are multiple disconnected areas due to forbidden blocks,
        # we connect them by starting DFS from remaining unvisited free cells.
        for y in range(grid.grid_height):
            for x in range(grid.grid_width):
                cell = grid[x, y]
                if cell.forbidden or cell.visited:
                    continue
                # connect this component to an existing visited neighbor if possible
                self._connect_to_visited_neighbor(grid, cell)
                self._dfs_from(grid, (x, y))

        self._clear_visited(grid)

    def _dfs_from(self, grid: Grid, start: Coord) -> None:
        """Run DFS from a start cell, carving passages among non-forbidden cells."""
        sx, sy = start
        stack: List[Cell] = []
        current = grid[sx, sy]
        current.visited = True
        stack.append(current)

        while stack:
            current = stack[-1]
            unvisited = self._unvisited_neighbors(grid, current)
            if not unvisited:
                stack.pop()
                continue

            direction, nxt = random.choice(unvisited)
            self._carve_passage(current, nxt, direction)
            nxt.visited = True
            stack.append(nxt)

    def _reset_grid(self, grid: Grid) -> None:
        """Reset grid walls/flags but keep forbidden flag intact."""
        for row in grid.matrix:
            for cell in row:
                cell.paths["north"] = True
                cell.paths["east"] = True
                cell.paths["south"] = True
                cell.paths["west"] = True
                cell.visited = False

    def _clear_visited(self, grid: Grid) -> None:
        """Clear visited flags after generation."""
        for row in grid.matrix:
            for cell in row:
                cell.visited = False

    def _first_free_cell(self, grid: Grid) -> Coord:
        """Return first non-forbidden cell coordinate; fallback to (0,0)."""
        for y in range(grid.grid_height):
            for x in range(grid.grid_width):
                if not grid[x, y].forbidden:
                    return (x, y)
        return (0, 0)

    def _unvisited_neighbors(self, grid: Grid, cell: Cell) -> List[Tuple[str, Cell]]:
        """Return in-bounds, non-forbidden, unvisited neighbors."""
        out: List[Tuple[str, Cell]] = []
        x, y = cell.cell_x, cell.cell_y

        for direction, (dx, dy) in self.DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < grid.grid_width and 0 <= ny < grid.grid_height):
                continue
            ncell = grid[nx, ny]
            if ncell.forbidden or ncell.visited:
                continue
            out.append((direction, ncell))

        return out

    def _connect_to_visited_neighbor(self, grid: Grid, cell: Cell) -> None:
        """
        If possible, open one wall between this unvisited free cell and an adjacent visited free cell.
        Helps keep maze mostly connected around forbidden blocks.
        """
        x, y = cell.cell_x, cell.cell_y
        candidates: List[Tuple[str, Cell]] = []

        for direction, (dx, dy) in self.DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < grid.grid_width and 0 <= ny < grid.grid_height):
                continue
            ncell = grid[nx, ny]
            if ncell.forbidden:
                continue
            if ncell.visited:
                candidates.append((direction, ncell))

        if candidates:
            direction, visited_cell = random.choice(candidates)
            # carve between cell (unvisited) and visited_cell
            # direction is from cell -> visited_cell
            self._carve_passage(cell, visited_cell, direction)

    def _carve_passage(self, a: Cell, b: Cell, direction_from_a: str) -> None:
        """Open passage between adjacent non-forbidden cells."""
        if a.forbidden or b.forbidden:
            return
        a.set_path(direction_from_a, False)
        b.set_path(self.OPPOSITE[direction_from_a], False)
