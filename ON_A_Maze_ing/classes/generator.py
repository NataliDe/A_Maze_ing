"""
Generator interface module.

Defines a common interface for all maze generation algorithms.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Tuple

from .grid import Grid

Coord = Tuple[int, int]


class MazeGenerator(ABC):
    """
    Base interface for maze generators.

    Implementations must modify the Grid in-place by opening/closing walls.

    Convention used in this project:
        cell.paths[dir] == True  -> wall CLOSED
        cell.paths[dir] == False -> passage OPEN
    """

    @abstractmethod
    def generate(self, grid: Grid, start: Optional[Coord] = None) -> None:
        """
        Generate a maze in-place.

        Args:
            grid: Grid to modify.
            start: Optional start coordinate (x, y).
            If None, generator chooses.

        Returns:
            None.
        """
        raise NotImplementedError
