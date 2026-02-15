"""
MazeWriter: saves maze in Moulinette-friendly format.

Format:
- H lines of W hex characters (each hex digit encodes walls: N=1,E=2,S=4,W=8).
- blank line
- entry "x,y"
- exit "x,y"
- path directions string (N/E/S/W), may be empty
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

from .cell import Cell
from .grid import Grid

Coord = Tuple[int, int]


@dataclass(frozen=True)
class SavePayload:
    """All data required to save maze output."""
    grid: Grid
    entry: Coord
    exit: Coord
    path_dirs: str


class MazeWriter:
    """Writes maze data to a file in required hex+coords+path format."""

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
        path_dirs: str = "",
    ) -> None:
        """
        Save maze to filename.

        Args:
            grid: Maze grid.
            filename: Output file name (relative or absolute).
            entry: (x,y) entry coordinate.
            exit_: (x,y) exit coordinate.
            path_dirs: Path directions string, e.g. "EESWNN...".
        """
        payload = SavePayload(
            grid=grid, entry=entry, exit=exit_, path_dirs=path_dirs)
        self._write_payload(filename, payload)

    def _write_payload(self, filename: str, payload: SavePayload) -> None:
        out_path = Path(filename)

        # Make sure parent exists (if user provided "out/maze.txt")
        try:
            if out_path.parent and str(out_path.parent) != ".":
                out_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise OSError(
                f"Cannot create output directory: {out_path.parent}") from exc

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
        Write H lines of W hex chars.

        Forbidden cells are still encoded as full walls (F),
        which is coherent (completely blocked).
        """
        for y in range(grid.grid_height):
            line_chars = []
            for x in range(grid.grid_width):
                cell = grid[x, y]
                val = self._encode_cell(cell)
                line_chars.append(f"{val:X}")  # uppercase hex digit
            f.write("".join(line_chars) + "\n")

    def _encode_cell(self, cell: Cell) -> int:
        """
        Encode cell walls into a nibble:
        N=1,E=2,S=4,W=8 are set when wall is CLOSED (True).
        """
        if cell.forbidden:
            return 0xF

        val = 0
        for direction, bit in self._BITS.items():
            if cell.paths.get(direction, True):
                val |= bit
        return val
