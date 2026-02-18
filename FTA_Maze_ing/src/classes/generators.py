"""
generators.py

Defines common generator interface and a registry used by Manager.
"""

from dataclasses import dataclass
from typing import Dict, Protocol, Tuple

from .grid import Grid

Coord = Tuple[int, int]


class MazeGenerator(Protocol):
    """Common interface for all maze generators."""
    name: str

    def generate(self, grid: Grid, start: Coord) -> None:
        """Generate maze in-place."""


@dataclass(frozen=True)
class GeneratorEntry:
    """Registry entry."""
    key: str
    title: str


class GeneratorRegistry:
    """Holds generator instances and cycles through them."""

    def __init__(self, generators: Dict[str, MazeGenerator], order: Tuple[str, ...]) -> None:
        self._generators = generators
        self._order = order
        self._idx = 0

    def current(self) -> MazeGenerator:
        return self._generators[self._order[self._idx]]

    def current_key(self) -> str:
        return self._order[self._idx]

    def next(self) -> MazeGenerator:
        self._idx = (self._idx + 1) % len(self._order)
        return self.current()
