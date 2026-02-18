"""
solver.py

BFS shortest path solver for the maze.

Assumption for this project:
- cell.paths[direction] == True means the passage is OPEN in that direction.
- cell.forbidden == True means cell is blocked.

Returns:
- list of cells forming the path (start..end)
- path as a string of directions: N/E/S/W
"""


from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Set, Tuple

from .grid import Grid

Coord = Tuple[int, int]


@dataclass(frozen=True)
class SolveResult:
    """Result of BFS solve."""
    path_coords: List[Coord]
    path_dirs: str


class Solver:
    """Shortest-path solver using BFS."""

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
        "south": "north",
        "east": "west",
        "west": "east",
    }

    def __init__(self, grid: Grid) -> None:
        self.grid = grid

    def solve(self, start: Coord, goal: Coord) -> SolveResult:
        """
        Solve the maze from start to goal.

        Args:
            start: (x, y)
            goal: (x, y)

        Returns:
            SolveResult(path_coords, path_dirs). Empty path if not found.
        """
        if not self._in_bounds(start) or not self._in_bounds(goal):
            return SolveResult([], "")

        sx, sy = start
        gx, gy = goal

        if self.grid.matrix[sy][sx].forbidden or self.grid.matrix[gy][gx].forbidden:
            return SolveResult([], "")

        q: Deque[Coord] = deque([start])
        visited: Set[Coord] = {start}
        prev: Dict[Coord, Optional[Coord]] = {start: None}
        prev_dir: Dict[Coord, Optional[str]] = {start: None}

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
        """Return reachable neighbors (through OPEN passages)."""
        x, y = coord
        cell = self.grid.matrix[y][x]
        if cell.forbidden:
            return []

        out: List[Tuple[str, Coord]] = []
        for direction, (dx, dy) in self._DIRS.items():
            nx, ny = x + dx, y + dy
            if not (0 <= nx < self.grid.grid_width and 0 <= ny < self.grid.grid_height):
                continue

            ncell = self.grid.matrix[ny][nx]
            if ncell.forbidden:
                continue

            # passage must be open in both directions (robust)
            if cell.paths.get(direction, False) is not True:
                continue
            opp = self._OPPOSITE[direction]
            if ncell.paths.get(opp, False) is not True:
                continue

            out.append((direction, (nx, ny)))
        return out

    def _reconstruct(
        self,
        prev: Dict[Coord, Optional[Coord]],
        prev_dir: Dict[Coord, Optional[str]],
        goal: Coord,
    ) -> SolveResult:
        coords: List[Coord] = []
        letters: List[str] = []

        cur: Optional[Coord] = goal
        while cur is not None:
            coords.append(cur)
            d = prev_dir.get(cur)
            if d is not None:
                letters.append(self._DIR_LETTER[d])
            cur = prev.get(cur)

        coords.reverse()
        letters.reverse()
        return SolveResult(coords, "".join(letters))

    def _in_bounds(self, coord: Coord) -> bool:
        x, y = coord
        return 0 <= x < self.grid.grid_width and 0 <= y < self.grid.grid_height
