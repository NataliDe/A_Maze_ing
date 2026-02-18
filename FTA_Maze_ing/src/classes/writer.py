"""
writer.py

Writes the maze to an output file in Moulinette-friendly format.

Format:
- H lines of W hex characters (each cell encoded as a hex digit)
- blank line
- entry "x,y"
- exit "x,y"
- path directions string (N/E/S/W) (may be empty, but recommended)

Encoding:
We encode WALLS using bits:
- N = 1
- E = 2
- S = 4
- W = 8

In this project, cell.paths[dir] == True means PASSAGE is OPEN.
So a wall is present when paths[dir] == False.
Forbidden cells are written as 'F' (0xF).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

from .grid import Grid

Coord = Tuple[int, int]


@dataclass(frozen=True)
class SavePayload:
    """All data required for saving maze output."""
    grid: Grid
    entry: Coord
    exit: Coord
    path_dirs: str


class MazeWriter:
    """Saves maze state to a text file."""

    _BITS: Dict[str, int] = {
        "north": 1,
        "east": 2,
        "south": 4,
        "west": 8,
    }

    def save(
        self,
        grid: Grid,
        filename: str,
        entry: Coord,
        exit_: Coord,
        path_dirs: str,
    ) -> None:
        """
        Save maze to file.

        Args:
            grid: Grid object.
            filename: output file path/name.
            entry: (x, y)
            exit_: (x, y)
            path_dirs: string like "EESWN..."
        """
        payload = SavePayload(grid=grid, entry=entry, exit=exit_, path_dirs=path_dirs)
        self._write(filename, payload)

    def _write(self, filename: str, payload: SavePayload) -> None:
        out_path = Path(filename)

        try:
            if str(out_path.parent) not in ("", "."):
                out_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise OSError(f"Cannot create output directory: {out_path.parent}") from exc

        try:
            with out_path.open("w", encoding="utf-8") as f:
                self._write_hex_grid(f, payload.grid)
                f.write("\n")
                f.write(f"{payload.entry[0]},{payload.entry[1]}\n")
                f.write(f"{payload.exit[0]},{payload.exit[1]}\n")
                f.write(payload.path_dirs + "\n")
        except OSError as exc:
            raise OSError(f"Cannot write output file: {out_path}") from exc

    def _write_hex_grid(self, f, grid: Grid) -> None:
        """
        Write H rows of W hex chars.

        Forbidden cells are written as 'F' (all walls present).
        """
        for y in range(grid.grid_height):
            row_chars = []
            for x in range(grid.grid_width):
                cell = grid.matrix[y][x]
                val = self._encode_cell(cell)
                row_chars.append(f"{val:X}")  # uppercase hex
            f.write("".join(row_chars) + "\n")

    def _encode_cell(self, cell) -> int:
        """
        Encode a cell into a nibble where bits represent WALLS.

        Wall present if cell.paths[dir] is False.
        """
        if getattr(cell, "forbidden", False):
            return 0xF

        val = 0
        for direction, bit in self._BITS.items():
            is_open = bool(cell.paths.get(direction, False))
            if not is_open:
                val |= bit
        return val
