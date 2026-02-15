"""
Grid module.

Contains the Grid class that stores a 2D matrix of Cell objects
and provides basic helpers like indexing and neighbor lookup.
"""

from __future__ import annotations

from typing import List, Tuple

from .cell import Cell

Coord = Tuple[int, int]


class Grid:
    """
    2D grid of maze cells.

    Attributes:
        grid_width: Number of columns.
        grid_height: Number of rows.
        matrix: 2D list of Cell objects indexed as matrix[y][x].
    """

    def __init__(self, grid_width: int, grid_height: int) -> None:
        """
        Initialize a grid with cells.

        Args:
            grid_width: Grid width (X dimension).
            grid_height: Grid height (Y dimension).
        """
        self.grid_width: int = grid_width
        self.grid_height: int = grid_height
        self.matrix: List[List[Cell]] = [
            [Cell(x, y) for x in range(self.grid_width)]
            for y in range(self.grid_height)
        ]

    def __getitem__(self, item: Coord) -> Cell:
        """
        Access a cell by (x, y).

        Args:
            item: (x, y) coordinate.

        Returns:
            Cell at the given coordinate.
        """
        x, y = item
        return self.matrix[y][x]

    def __repr__(self) -> str:
        """
        Return short grid info useful for logs.

        Returns:
            String representation.
        """
        return (
            f"Grid = {self.grid_width}x{self.grid_height}\n"
            f"Cells = {self.grid_width * self.grid_height}"
        )

    def display(self) -> None:
        """
        Quick console check of the grid shape.

        This is a debug helper.
        """
        for row in self.matrix:
            print(" ".join("[ ]" for _ in row))

    def get_neighbors(self, item: Coord) -> List[Cell]:
        """
        Return in-bounds neighboring cells (N, E, S, W), without wall checks.

        Args:
            item: (x, y) coordinate.

        Returns:
            List of neighboring Cell objects.
        """
        x, y = item
        neighbors: List[Cell] = []

        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                neighbors.append(self[nx, ny])

        return neighbors

    def get_info(self) -> str:
        """
        Return internal state for debugging.

        Returns:
            Dict string representation.
        """
        return str(self.__dict__)
