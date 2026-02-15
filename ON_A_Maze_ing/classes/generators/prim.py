"""
Randomized Prim generator.

Creates a maze using randomized Prim's algorithm, skipping forbidden cells.
"""

from __future__ import annotations

import random
from typing import Dict, List, Tuple

from ..cell import Cell
from ..generator import Coord, MazeGenerator
from ..grid import Grid

FrontierItem = Tuple[Cell, Cell, str]
# (from_visited_cell, frontier_cell, direction_from_visited_to_frontier)


class PrimGenerator(MazeGenerator):
    """
    Maze generator (Randomized Prim) skipping forbidden cells.
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
        Generate a maze in-place. Forbidden cells remain solid obstacles.

        Args:
            grid: Grid to modify.
            start: Optional start coordinate. Defaults to first non-forbidden.

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

        start_cell = grid[sx, sy]
        start_cell.visited = True

        frontier: List[FrontierItem] = []
        self._add_frontier_edges(grid, start_cell, frontier)

        while frontier:
            from_cell, to_cell, direction = random.choice(frontier)
            frontier.remove((from_cell, to_cell, direction))

            if to_cell.visited or to_cell.forbidden:
                continue

            self._carve_passage(from_cell, to_cell, direction)
            to_cell.visited = True

            self._add_frontier_edges(grid, to_cell, frontier)

        # If there are isolated free regions (due to forbidden blocks), connect them:
        for y in range(grid.grid_height):
            for x in range(grid.grid_width):
                cell = grid[x, y]
                if cell.forbidden or cell.visited:
                    continue
                self._connect_to_visited_neighbor(grid, cell)
                cell.visited = True
                self._add_frontier_edges(grid, cell, frontier)
                while frontier:
                    f_from, f_to, f_dir = random.choice(frontier)
                    frontier.remove((f_from, f_to, f_dir))
                    if f_to.visited or f_to.forbidden:
                        continue
                    self._carve_passage(f_from, f_to, f_dir)
                    f_to.visited = True
                    self._add_frontier_edges(grid, f_to, frontier)

        self._clear_visited(grid)

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

    def _add_frontier_edges(
        self,
        grid: Grid,
        cell: Cell,
        frontier: List[FrontierItem],
    ) -> None:
        """Add edges from a visited cell to its unvisited, non-forbidden neighbors."""
        x, y = cell.cell_x, cell.cell_y

        for direction, (dx, dy) in self.DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < grid.grid_width and 0 <= ny < grid.grid_height):
                continue

            ncell = grid[nx, ny]
            if ncell.forbidden or ncell.visited:
                continue

            frontier.append((cell, ncell, direction))

    def _connect_to_visited_neighbor(self, grid: Grid, cell: Cell) -> None:
        """Connect an unvisited free cell to a random adjacent visited free cell."""
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
            self._carve_passage(cell, visited_cell, direction)

    def _carve_passage(self, a: Cell, b: Cell, direction_from_a: str) -> None:
        """Open passage between adjacent non-forbidden cells."""
        if a.forbidden or b.forbidden:
            return
        a.set_path(direction_from_a, False)
        b.set_path(self.OPPOSITE[direction_from_a], False)
