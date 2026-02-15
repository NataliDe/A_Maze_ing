"""
Origin Shift generator.

Implements Origin Shift using a spanning tree, skipping forbidden cells.
Forbidden cells remain solid obstacles (no passages carved through them).
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

from ..cell import Cell
from ..generator import Coord, MazeGenerator
from ..grid import Grid

CoordKey = Tuple[int, int]
ParentMap = Dict[CoordKey, Optional[CoordKey]]


class OriginShiftGenerator(MazeGenerator):
    """Origin Shift generator that ignores forbidden cells."""

    DIRS: Dict[str, Coord] = {
        "north": (0, -1),
        "east": (1, 0),
        "south": (0, 1),
        "west": (-1, 0),
    }

    def __init__(self, iterations_multiplier: int = 10) -> None:
        self.iterations_multiplier: int = iterations_multiplier

    def generate(self, grid: Grid, start: Coord | None = None) -> None:
        """
        Generate maze in-place while keeping forbidden cells blocked.
        """
        self._reset_grid(grid)

        free_cells = self._free_coords(grid)
        if not free_cells:
            return

        parent = self._seed_parent_map_for_free(grid, free_cells)
        origin = self._find_origin(parent)

        steps = len(free_cells) * self.iterations_multiplier
        for _ in range(steps):
            origin = self._origin_shift_step(grid, parent, origin)

        self._apply_tree_to_walls(grid, parent)

        for row in grid.matrix:
            for cell in row:
                cell.visited = False

    def _reset_grid(self, grid: Grid) -> None:
        """Reset walls/visited but keep forbidden flag intact."""
        for row in grid.matrix:
            for cell in row:
                cell.paths["north"] = True
                cell.paths["east"] = True
                cell.paths["south"] = True
                cell.paths["west"] = True
                cell.visited = False

    def _free_coords(self, grid: Grid) -> List[CoordKey]:
        """List all non-forbidden coordinates."""
        out: List[CoordKey] = []
        for y in range(grid.grid_height):
            for x in range(grid.grid_width):
                if not grid[x, y].forbidden:
                    out.append((x, y))
        return out

    def _neighbors_free(self, grid: Grid, coord: CoordKey) -> List[CoordKey]:
        """Neighbors of coord that are non-forbidden."""
        x, y = coord
        out: List[CoordKey] = []
        for dx, dy in self.DIRS.values():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < grid.grid_width and 0 <= ny < grid.grid_height):
                continue
            if grid[nx, ny].forbidden:
                continue
            out.append((nx, ny))
        return out

    def _seed_parent_map_for_free(self, grid: Grid, free_cells: List[CoordKey]) -> ParentMap:
        """
        Build an initial spanning forest over free cells:
        - For each free cell, try to set parent to a free neighbor to the right,
          else down, else left, else up; the last chosen as origin (parent=None).
        """
        free_set = set(free_cells)
        parent: ParentMap = {}

        # pick an origin candidate: bottom-rightmost free cell
        origin = max(free_cells, key=lambda p: (p[1], p[0]))
        parent[origin] = None

        # naive parent assignment: for all others, point "roughly" toward origin
        for (x, y) in free_cells:
            if (x, y) == origin:
                continue

            candidates = [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)]
            chosen: Optional[CoordKey] = None
            for c in candidates:
                if c in free_set:
                    chosen = c
                    break
            if chosen is None:
                # isolated free cell
                parent[(x, y)] = None
            else:
                parent[(x, y)] = chosen

        # ensure exactly one origin per connected component is fine; algorithm will work as forest,
        # and _apply_tree_to_walls opens edges for nodes that have parent != None.
        return parent

    def _find_origin(self, parent: ParentMap) -> CoordKey:
        """Return any coordinate with parent None."""
        for coord, p in parent.items():
            if p is None:
                return coord
        return next(iter(parent.keys()))

    def _origin_shift_step(self, grid: Grid, parent: ParentMap, origin: CoordKey) -> CoordKey:
        """
        Perform one origin shift step among free neighbors.
        If no free neighbors, keep origin.
        """
        neighs = self._neighbors_free(grid, origin)
        if not neighs:
            return origin

        nxt = random.choice(neighs)
        parent[origin] = nxt
        parent[nxt] = None
        return nxt

    def _apply_tree_to_walls(self, grid: Grid, parent: ParentMap) -> None:
        """Open passages for parent edges, skipping any forbidden cells."""
        for (x, y), p in parent.items():
            if p is None:
                continue
            px, py = p

            a = grid[x, y]
            b = grid[px, py]
            if a.forbidden or b.forbidden:
                continue
            self._open_between(a, b)

    def _open_between(self, a: Cell, b: Cell) -> None:
        """Open passage between adjacent cells."""
        dx = b.cell_x - a.cell_x
        dy = b.cell_y - a.cell_y

        if dx == 1 and dy == 0:
            a.set_path("east", False)
            b.set_path("west", False)
        elif dx == -1 and dy == 0:
            a.set_path("west", False)
            b.set_path("east", False)
        elif dx == 0 and dy == 1:
            a.set_path("south", False)
            b.set_path("north", False)
        elif dx == 0 and dy == -1:
            a.set_path("north", False)
            b.set_path("south", False)
