"""
kruskal_generator.py

Randomized Kruskal's algorithm generator (perfect maze).
"""

import random
from typing import Dict, List, Tuple

from .grid import Grid

Coord = Tuple[int, int]


class KruskalGenerator:
    """Kruskal generator using Union-Find."""

    name = "kruskal"

    _EDGES_DIRS = (
        ("east", (1, 0)),
        ("south", (0, 1)),
    )

    _OPPOSITE = {
        "north": "south",
        "south": "north",
        "east": "west",
        "west": "east",
    }

    def generate(self, grid: Grid, start: Coord) -> None:
        self._reset_grid(grid)

        parent: Dict[Coord, Coord] = {}
        rank: Dict[Coord, int] = {}
        nodes: List[Coord] = []

        for y in range(grid.grid_height):
            for x in range(grid.grid_width):
                if grid.matrix[y][x].forbidden:
                    continue
                c = (x, y)
                nodes.append(c)
                parent[c] = c
                rank[c] = 0

        edges: List[Tuple[Coord, Coord, str]] = []
        for y in range(grid.grid_height):
            for x in range(grid.grid_width):
                if grid.matrix[y][x].forbidden:
                    continue
                for d, (dx, dy) in self._EDGES_DIRS:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < grid.grid_width and 0 <= ny < grid.grid_height:
                        if grid.matrix[ny][nx].forbidden:
                            continue
                        edges.append(((x, y), (nx, ny), d))

        random.shuffle(edges)

        for a, b, d in edges:
            ra = self._find(parent, a)
            rb = self._find(parent, b)
            if ra == rb:
                continue
            self._union(parent, rank, ra, rb)
            self._carve(grid, a, b, d)

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

    def _find(self, parent: Dict[Coord, Coord], x: Coord) -> Coord:
        if parent[x] != x:
            parent[x] = self._find(parent, parent[x])
        return parent[x]

    def _union(self, parent: Dict[Coord, Coord], rank: Dict[Coord, int], a: Coord, b: Coord) -> None:
        if rank[a] < rank[b]:
            parent[a] = b
        elif rank[a] > rank[b]:
            parent[b] = a
        else:
            parent[b] = a
            rank[a] += 1

    def _carve(self, grid: Grid, a: Coord, b: Coord, d: str) -> None:
        ax, ay = a
        bx, by = b
        cell = grid.matrix[ay][ax]
        ncell = grid.matrix[by][bx]
        cell.paths[d] = True
        ncell.paths[self._OPPOSITE[d]] = True
