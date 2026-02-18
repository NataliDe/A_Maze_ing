"""
mlx_viewer.py

MLX viewer for maze.txt output.

Reads maze.txt in Moulinette format:
- H lines of W hex characters
- blank line (optional)
- entry "x,y"
- exit "x,y"
- path directions string (N/E/S/W)

Controls:
- ESC: close window
- ENTER: toggle showing solution path
- SPACE: randomize wall color
"""


from dataclasses import dataclass
from pathlib import Path
from random import randint
from typing import Dict, List, Tuple

from mlx import Mlx

from .maze_config import MazeConfig

Coord = Tuple[int, int]


@dataclass(frozen=True)
class MazeTxtData:
    """Parsed maze.txt content."""
    hex_rows: List[str]
    entry: Coord
    exit: Coord
    path_dirs: str


class MlxViewer:
    """Visualize maze.txt in an MLX window."""

    def __init__(self) -> None:
        self._mlx = Mlx()

    def open_from_txt(self, config: MazeConfig) -> None:
        """
        Open MLX window and draw maze from config.output_file_name.

        Args:
            config: MazeConfig used for width/height validation + file name.
        """
        maze_path = Path(config.output_file_name)
        data = self._read_maze_txt(maze_path, config.maze_width, config.maze_height)

        mlx_ptr = self._mlx.mlx_init()

        win_w, win_h = 1500, 800
        img_h = win_h - 50

        window = self._mlx.mlx_new_window(mlx_ptr, win_w, win_h, "A-MAZE-ING (MLX)")
        image = self._mlx.mlx_new_image(mlx_ptr, win_w, img_h)
        image_address, _bpp, size_line, _fmt = self._mlx.mlx_get_data_addr(image)

        scale = self._compute_scale(win_w, img_h, config.maze_width, config.maze_height)
        path_coords = self._path_to_coords(data.entry, data.path_dirs)

        state: Dict[str, object] = {
            "mlx_ptr": mlx_ptr,
            "window": window,
            "image": image,
            "image_address": image_address,
            "size_line": int(size_line),
            "scale": int(scale),
            "hex_rows": data.hex_rows,
            "entry": data.entry,
            "exit": data.exit,
            "path": path_coords,
            "show_path": False,
            "wall_color": bytes([255, 255, 255, 255]),
        }

        self._draw(state)

        self._mlx.mlx_string_put(
            mlx_ptr,
            window,
            20,
            img_h + 5,
            0xFFFFFFFF,
            "ESC: quit | ENTER: toggle path | SPACE: random wall color",
        )

        self._mlx.mlx_key_hook(window, self._on_key, state)
        self._mlx.mlx_loop(mlx_ptr)

    # ---------------- parsing ----------------

    def _read_maze_txt(self, path: Path, w: int, h: int) -> MazeTxtData:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise OSError(f"Cannot read maze file: {path}") from exc

        if len(lines) < h + 2:
            raise ValueError("maze.txt is too short or corrupted")

        hex_rows = lines[:h]
        for row in hex_rows:
            if len(row) != w:
                raise ValueError("maze.txt grid size mismatch with config")
            for ch in row:
                if ch.upper() not in "0123456789ABCDEF":
                    raise ValueError("maze.txt contains non-hex characters")

        idx = h
        while idx < len(lines) and lines[idx].strip() == "":
            idx += 1

        entry = self._parse_coord(lines, idx, "entry")
        exit_ = self._parse_coord(lines, idx + 1, "exit")

        path_dirs = ""
        if idx + 2 < len(lines):
            path_dirs = lines[idx + 2].strip()

        return MazeTxtData(hex_rows=hex_rows, entry=entry, exit=exit_, path_dirs=path_dirs)

    @staticmethod
    def _parse_coord(lines: List[str], idx: int, label: str) -> Coord:
        try:
            x_s, y_s = lines[idx].split(",", 1)
            return (int(x_s), int(y_s))
        except Exception as exc:
            raise ValueError(f"Bad {label} coord line in maze.txt") from exc

    # ---------------- helpers ----------------

    @staticmethod
    def _compute_scale(win_w: int, img_h: int, w: int, h: int) -> int:
        # fit W x H blocks into window
        scale_h = max(1, img_h // max(1, h))
        scale_w = max(1, win_w // max(1, w))
        return max(2, min(scale_h, scale_w))

    @staticmethod
    def _path_to_coords(start: Coord, path_dirs: str) -> List[Coord]:
        coords: List[Coord] = [start]
        for ch in path_dirs:
            x, y = coords[-1]
            if ch == "E":
                coords.append((x + 1, y))
            elif ch == "S":
                coords.append((x, y + 1))
            elif ch == "W":
                coords.append((x - 1, y))
            elif ch == "N":
                coords.append((x, y - 1))
        return coords

    # ---------------- input ----------------

    def _on_key(self, keycode: int, state: Dict[str, object]) -> None:
        mlx_ptr = state["mlx_ptr"]
        window = state["window"]

        # ESC
        if keycode == 65307:
            self._mlx.mlx_destroy_window(mlx_ptr, window)
            self._mlx.mlx_loop_exit(mlx_ptr)
            return

        # SPACE -> random wall color
        if keycode == 32:
            state["wall_color"] = bytes(
                [randint(0, 255), randint(0, 255), randint(0, 255), 255]
            )

        # ENTER -> toggle path
        if keycode == 65293:
            state["show_path"] = not bool(state["show_path"])

        self._draw(state)

    # ---------------- drawing ----------------

    def _draw(self, state: Dict[str, object]) -> None:
        mlx_ptr = state["mlx_ptr"]
        window = state["window"]
        image = state["image"]
        image_address = state["image_address"]
        size_line = int(state["size_line"])
        scale = int(state["scale"])
        hex_rows = state["hex_rows"]
        entry = state["entry"]
        exit_ = state["exit"]
        path = state["path"]
        show_path = bool(state["show_path"])
        wall_color = state["wall_color"]

        # clear (black)
        image_address[:] = bytes([0, 0, 0, 255]) * (len(image_address) // 4)

        # path (cyan)
        if show_path:
            for px, py in path:
                self._fill_cell(image_address, scale, size_line, px, py, bytes([0, 255, 255, 255]))

        # start (red) / end (green)
        self._fill_cell(image_address, scale, size_line, entry[0], entry[1], bytes([255, 0, 0, 255]))
        self._fill_cell(image_address, scale, size_line, exit_[0], exit_[1], bytes([0, 255, 0, 255]))

        # forbidden cells (F) - purple
        for row_idx, row in enumerate(hex_rows):
            for col_idx, ch in enumerate(row):
                if ch.upper() == "F":
                    self._fill_cell(image_address, scale, size_line, col_idx, row_idx, bytes([150, 0, 255, 255]))

        # walls from hex
        for row_idx, row in enumerate(hex_rows):
            for col_idx, ch in enumerate(row):
                self._draw_walls(ch, row_idx, col_idx, size_line, scale, image_address, wall_color)

        self._mlx.mlx_put_image_to_window(mlx_ptr, window, image, 0, 0)

    @staticmethod
    def _fill_cell(image_address, scale: int, size_line: int, x: int, y: int, color: bytes) -> None:
        off_x = scale * x * 4
        off_y = scale * size_line * y
        for i in range(scale):
            start = off_x + off_y + i * size_line
            image_address[start:start + scale * 4] = color * scale

    @staticmethod
    def _draw_walls(
        block_hex: str,
        row_idx: int,
        col_idx: int,
        size_line: int,
        scale: int,
        image_address,
        color: bytes,
    ) -> None:
        """
        Draw walls for a cell using bits (WALLS):
        N=1, E=2, S=4, W=8 (bit set -> wall is present).
        """
        try:
            val = int(block_hex, 16)
        except ValueError:
            return

        has_n = (val & 1) != 0
        has_e = (val & 2) != 0
        has_s = (val & 4) != 0
        has_w = (val & 8) != 0

        off_x = scale * col_idx * 4
        off_y = scale * size_line * row_idx

        # north
        if has_n:
            image_address[off_x + off_y:off_x + off_y + scale * 4] = color * scale

        # south
        if has_s:
            base = off_y + (scale - 1) * size_line
            image_address[off_x + base:off_x + base + scale * 4] = color * scale

        # west/east
        for i in range(scale):
            line_base = off_y + i * size_line
            if has_w:
                image_address[off_x + line_base:off_x + line_base + 4] = color
            if has_e:
                edge = off_x + line_base + (scale - 1) * 4
                image_address[edge:edge + 4] = color
