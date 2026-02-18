"""
Defines the atomic unit of the maze grid.
"""

from typing import Dict, Optional


class Cell:
    """Represents a single unit (square) within the maze grid.

        This class holds the state of a specific coordinate in the maze,
        including
        walls (paths), special flags (start/exit), and algorithm-specific data
        (visited status, vectors).

        Attributes:
            cell_x (int): The x-coordinate (column) of the cell in the grid.
            cell_y (int): The y-coordinate (row) of the cell in the grid.
            paths (Dict[str, bool]): A dictionary mapping cardinal directions
                ("north", "south", "east", "west") to boolean values.
                True indicates an open path (no wall), False indicates a wall.
            is_start (bool): True if this cell is the entry point of the maze.
            is_exit (bool): True if this cell is the exit point of the maze.
            visited (bool): Flag used by generation algorithms to
            track processing
                state or visual "chaos" propagation.
            forbidden (bool): True if the cell is part of a masked area
            (e.g., text)
                and cannot be part of the maze path.
            is_solution (bool): True if the cell is part of the
            solved path from
                Start to Exit. Used for rendering.
            vector (Optional[str]): The direction of the "flow"
            for algorithms like
                Origin Shift (Wilson's/Aldous-Broder variation). Points to the
                parent cell or flow direction ("north", "south", etc.).
        """
    def __init__(self, cell_x: int, cell_y: int) -> None:
        """Initializes a new Cell instance.

        Args:
            cell_x (int): The x-coordinate of the cell.
            cell_y (int): The y-coordinate of the cell.
        """
        self.cell_x: int = cell_x
        self.cell_y: int = cell_y
        self.paths: Dict[str, bool] = {
            "north": False,
            "east": False,
            "south": False,
            "west": False,
        }
        self.is_start: bool = False
        self.is_exit: bool = False
        self.visited: bool = False
        self.forbidden: bool = False
        self.is_solution: bool = False
        self.vector: Optional[str] = None

    def get_info(self) -> str:
        """Returns a string representation of the cell's current attributes.

        Useful for debugging purposes to inspect the state of the cell.

        Returns:
            str: A string containing the dictionary representation
            of the instance.
        """
        return str(self.__dict__)

    def set_path(self, direction: str, is_path: bool) -> None:
        """Updates the wall status for a specific direction.

        If the direction is valid, sets the path to open (True)
        or closed (False).
        Does nothing if the direction is invalid.

        Args:
            direction (str): The cardinal direction
            ("north", "south", "east", "west").
            is_path (bool): True to remove the wall (create a path),
                False to build a wall.
        """
        if direction in self.paths:
            self.paths[direction] = is_path
