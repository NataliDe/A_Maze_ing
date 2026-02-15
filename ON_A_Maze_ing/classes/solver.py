"""
Maze solver (BFS).

Finds the shortest path from entry to exit through open passages.
Forbidden cells are treated as blocked.
Produces:
- path_cells: list of Cell from start to end (inclusive)
- path_dirs: string of directions using 'N','E','S','W'
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Set, Tuple

from .cell import Cell
from .grid import Grid

Coord = Tuple[int, int]


@dataclass(frozen=True)
class SolveResult:
    """Result of solving the maze."""
    path_cells: List[Cell]
    path_dirs: str


class Solver:
    """Breadth-first search solver for the maze."""

    _DIRS: Dict[str, Coord] = {
        "north": (0, -1),
        "east": (1, 0),
        "south": (0, 1),
        "west": (-1, 0),
    }

    _DIR_LETTER: Dict[str, str] = {
        "north": "N",
        "east": "E",
        "south": "S",
        "west": "W",
    }

    _OPPOSITE: Dict[str, str] = {
        "north": "south",
        "east": "west",
        "south": "north",
        "west": "east",
    }

    def __init__(self, grid: Grid) -> None:
        self.grid: Grid = grid

    def solve(self, start: Coord, goal: Coord) -> SolveResult:
        """
        Solve maze using BFS.

        Args:
            start: (x,y) start coordinate.
            goal: (x,y) goal coordinate.

        Returns:
            SolveResult with path_cells and path_dirs. Empty path if not found.
        """
        if not self._in_bounds(start) or not self._in_bounds(goal):
            return SolveResult([], "")

        sx, sy = start
        gx, gy = goal

        if self.grid[sx, sy].forbidden or self.grid[gx, gy].forbidden:
            return SolveResult([], "")

        prev: Dict[Coord, Optional[Coord]] = {start: None}
        prev_dir: Dict[Coord, Optional[str]] = {start: None}

        q: Deque[Coord] = deque([start])
        visited: Set[Coord] = {start}

        while q:
            cur = q.popleft()
            if cur == goal:
                return self._reconstruct(prev, prev_dir, goal)

            for direction, nxt in self._neighbors(cur):
                if nxt in visited:
                    continue
                visited.add(nxt)
                prev[nxt] = cur
                prev_dir[nxt] = direction
                q.append(nxt)

        return SolveResult([], "")

    def _neighbors(self, coord: Coord) -> List[Tuple[str, Coord]]:
        """
        List reachable neighbors from coord through open passages.

        Passage is open if current cell wall is False in that direction.
        Also ensures neighbor is not
        forbidden and the opposite wall is open/consistent.
        """
        x, y = coord
        cell = self.grid[x, y]

        if cell.forbidden:
            return []

        out: List[Tuple[str, Coord]] = []
        for direction, (dx, dy) in self._DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < self.grid.grid_width
                    and 0 <= ny < self.grid.grid_height):
                continue

            ncell = self.grid[nx, ny]
            if ncell.forbidden:
                continue

            # must be open from current -> neighbor
            if cell.paths.get(direction, True) is True:
                continue

            # and also open from neighbor -> current (robustness)
            opp = self._OPPOSITE[direction]
            if ncell.paths.get(opp, True) is True:
                continue

            out.append((direction, (nx, ny)))
        return out

    def _reconstruct(
        self,
        prev: Dict[Coord, Optional[Coord]],
        prev_dir: Dict[Coord, Optional[str]],
        goal: Coord,
    ) -> SolveResult:
        """Reconstruct path from prev maps."""
        coords: List[Coord] = []
        dirs: List[str] = []

        cur: Optional[Coord] = goal
        while cur is not None:
            coords.append(cur)
            d = prev_dir.get(cur)
            if d is not None:
                dirs.append(self._DIR_LETTER[d])
            cur = prev.get(cur)

        coords.reverse()
        dirs.reverse()

        path_cells: List[Cell] = [self.grid[x, y] for (x, y) in coords]
        path_dirs = "".join(dirs)
        return SolveResult(path_cells=path_cells, path_dirs=path_dirs)

    def _in_bounds(self, coord: Coord) -> bool:
        x, y = coord
        return 0 <= x < self.grid.grid_width and 0 <= y < self.grid.grid_height
