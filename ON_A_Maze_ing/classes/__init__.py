"""
Classes package for the A-Maze-ing project.

Exports public classes used by the entry point and other modules.
"""

from __future__ import annotations

from .cell import Cell
from .generator import MazeGenerator
from .graphics import Graphics
from .grid import Grid
from .manager import Manager
from .maze_config import MazeConfig
from .menu import Menu
from .renderer import Renderer
from .solver import Solver
from .writer import MazeWriter

from .generators import DFSBacktrackerGenerator
from .generators import OriginShiftGenerator, PrimGenerator

__all__ = [
    "Cell",
    "Grid",
    "MazeConfig",
    "Menu",
    "Graphics",
    "Renderer",
    "Solver",
    "MazeGenerator",
    "DFSBacktrackerGenerator",
    "PrimGenerator",
    "OriginShiftGenerator",
    "MazeWriter",
    "Manager",
]
