"""
Cell module.

Defines the Cell class that represents one maze cell with walls and flags.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Cell:
    """
    One cell in the maze grid.

    Attributes:
        cell_x: X coordinate (column).
        cell_y: Y coordinate (row).
        paths: Dict of wall states.
        True means wall is CLOSED, False means OPEN.
        is_start: Whether this cell is the entry.
        is_exit: Whether this cell is the exit.
        visited: Helper flag used by some generators/algorithms.
        forbidden: Optional flag for future features.
    """

    cell_x: int
    cell_y: int
    paths: Dict[str, bool] = field(
        default_factory=lambda: {
            "north": True,
            "east": True,
            "south": True,
            "west": True,
        }
    )
    is_start: bool = False
    is_exit: bool = False
    visited: bool = False
    forbidden: bool = False

    def get_info(self) -> str:
        """
        Return string representation of internal state.

        Returns:
            Debug string.
        """
        return str(self.__dict__)

    def set_path(self, direction: str, is_path: bool) -> None:
        """
        Set wall state for a direction.

        Args:
            direction: One of: 'north', 'east', 'south', 'west'.
            is_path: Wall state;
            True means CLOSED wall, False means OPEN passage.

        Returns:
            None.
        """
        if direction in self.paths:
            self.paths[direction] = is_path
