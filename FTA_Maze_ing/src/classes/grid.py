"""
Defines the grid structure for the maze.
"""

from .cell import Cell
from .maze_config import MazeConfig
from typing import List, Tuple


class Grid:
    """Represents the 2D map of the maze.

    This class manages the collection of Cell objects,
    handles coordinate systems,
    defines boundaries, and manages special zones (like the start, exit, and
    forbidden areas).

    Attributes:
        grid_width (int): The width of the maze (number of columns).
        grid_height (int): The height of the maze (number of rows).
        matrix (List[List[Cell]]): A 2D list storing Cell objects.
            Access structure is matrix[y][x].
        perfection (bool): Indicates if the maze should be perfect (no loops)
            or imperfect (braid).
    """
    matrix = []

    def __init__(self, config: MazeConfig) -> None:
        """Initializes the Grid based on the provided configuration.

        Creates the 2D matrix of cells, sets the start and exit points,
        and applies the 'easter egg' mask if space permits.

        Args:
            config (MazeConfig): Configuration object containing dimensions,
                entry/exit points, and perfection settings.
        """
        self.grid_width: int = config.maze_width
        self.grid_height: int = config.maze_height

        # Initialize matrix: rows (y) of columns (x)
        self.matrix: List[List[Cell]] = [
            [Cell(x, y) for x in range(self.grid_width)]
            for y in range(self.grid_height)
        ]

        start_x, start_y = config.maze_entry
        exit_x, exit_y = config.maze_exit

        # Validate and set Start/Exit flags
        # Note: We assume config coordinates are within bounds
        # based on config validation
        self.matrix[start_y][start_x].is_start = True
        self.matrix[exit_y][exit_x].is_exit = True

        self.perfection: bool = config.maze_perfect

        self.easter_egg()

    def __getitem__(self, item: Tuple[int, int]) -> Cell:
        """Allows accessing cells using grid coordinates (x, y).

        Internally, the matrix is stored as row-major (y, x), but this method
        provides an abstraction for Cartesian access (x, y).

        Args:
            item (Tuple[int, int]): A tuple containing (x, y) coordinates.

        Returns:
            Cell: The cell object at the specified coordinates.
        """
        x, y = item
        return self.matrix[y][x]

    def __repr__(self) -> str:
        """Returns a concise string representation of the grid dimensions.

        Returns:
            str: A formatted string like "Grid = 20x20\nCells = 400".
        """
        return (f"Grid = {self.grid_width}x{self.grid_height}\n"
                f"Cells = {self.grid_width * self.grid_height}")

    def get_neighbors(self, item: Tuple[int, int]) -> List[Cell]:
        """Retrieves valid orthogonal neighbors for a specific coordinate.

        Checks all four cardinal directions (North, South, East, West) and
        returns only those cells that are within the grid boundaries.

        Args:
            item (Tuple[int, int]): A tuple containing the (x, y) coordinates
                of the center cell.

        Returns:
            List[Cell]: A list of adjacent Cell objects.
        """
        x, y = item
        neighbors = []

        # Deltas: (dx, dy) -> North, South, East, West
        direction = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        for dx, dy in direction:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                neighbors.append(self[nx, ny])

        return neighbors

    def get_info(self) -> str:
        """Returns a string representation of the instance's attributes.

        Returns:
            str: A string containing the dictionary representation
            of the instance.
        """
        return str(self.__dict__)

    def easter_egg(self) -> None:
        """Embeds a hidden '42' pattern into the center of the maze.

        This method marks specific cells forming the number '42' as forbidden
        and visited. This forces the generation algorithm to route paths around
        these cells, creating a visual obstacle in the shape of the number.

        If the grid is too small to contain the mask (plus a 1-cell border),
        the operation is skipped.
        """
        mask = [
            "x...xxx",
            "x.x...x",
            "xxx.xxx",
            "..x.x..",
            "..x.xxx"
        ]

        mask_height = len(mask)  # 5
        mask_width = len(mask[0])  # 7

        # Ensure there is at least 1 cell padding around the mask
        if (self.grid_width < mask_width + 2 or
                self.grid_height < mask_height + 2):
            return

        start_x = (self.grid_width - mask_width) // 2
        start_y = (self.grid_height - mask_height) // 2

        for row_idx, line in enumerate(mask):
            for col_idx, char in enumerate(line):
                if char == 'x':
                    grid_x = start_x + col_idx
                    grid_y = start_y + row_idx

                    cell = self.matrix[grid_y][grid_x]
                    cell.forbidden = True
                    # Marking as visited ensures algorithms
                    # don't try to process it
                    cell.visited = True
