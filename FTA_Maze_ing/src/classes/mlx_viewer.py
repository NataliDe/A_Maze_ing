"""
mlx_viewer.py

MLX viewer for maze.txt output with AUTO-SCALE, padding, and centering.
Lazy-loads MLX so the project can run even if MLX is not available.

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
    """Visualize maze.txt in an MLX window (lazy init)."""

    # Window defaults (safe for most screens)
    _WIN_W = 1200
    _WIN_H = 800
    _UI_H = 60            # bottom text area height
    _PADDING = 20         # outer padding for maze area
    _MIN_SCALE = 2        # smallest cell size in pixels

    def __init__(self) -> None:
        self._mlx = None  # initialized lazily

    def _get_mlx(self):
        """
        Lazy-load MLX so terminal version works even without MLX.

        Raises:
            RuntimeError: if MLX module or shared library cannot be loaded.
        """
        if self._mlx is not None:
            return self._mlx

        try:
            from mlx import Mlx  # local import by design
        except Exception as exc:
            raise RuntimeError(
                "MLX python module is not available. "
                "Install/compile MLX first (Linux recommended)."
            ) from exc

        try:
            self._mlx = Mlx()
        except OSError as exc:
            raise RuntimeError(
                "MLX shared library failed to load (ctypes CDLL). "
                "Missing libmlx.so / wrong path / missing system deps."
            ) from exc

        return self._mlx

    def open_from_txt(self, config: MazeConfig) -> None:
        """
        Open MLX window and draw maze from config.output_file_name.

        Args:
            config: MazeConfig used for width/height validation + file name.
        """
        maze_path = Path(config.output_file_name)
        data = self._read_maze_txt(maze_path, config.maze_width, config.maze_height)

        mlx = self._get_mlx()
        mlx_ptr = mlx.mlx_init()

        win_w = self._WIN_W
        win_h = self._WIN_H
        img_h = win_h - self._UI_H

        window = mlx.mlx_new_window(mlx_ptr, win_w, win_h, "A-MAZE-ING (MLX)")
        image = mlx.mlx_new_image(mlx_ptr, win_w, img_h)
        image_address, _bpp, size_line, _fmt = mlx.mlx_get_data_addr(image)

        layout = self._compute_layout(
            win_w=win_w,
            img_h=img_h,
            grid_w=config.maze_width,
            grid_h=config.maze_height,
        )
        path_coords = self._path_to_coords(data.entry, data.path_dirs)

        state: Dict[str, object] = {
            "mlx": mlx,
            "mlx_ptr": mlx_ptr,
            "window": window,
            "image": image,
            "image_address": image_address,
            "size_line": int(size_line),
            "scale": int(layout["scale"]),
            "off_x": int(layout["off_x"]),
            "off_y": int(layout["off_y"]),
            "hex_rows": data.hex_rows,
            "entry": data.entry,
            "exit": data.exit,
            "path": path_coords,
            "show_path": False,
            "wall_color": bytes([255, 255, 255, 255]),
        }

        self._draw(state)

        mlx.mlx_string_put(
            mlx_ptr,
            window,
            20,
            img_h + 10,
            0xFFFFFFFF,
            "ESC: quit | ENTER: toggle path | SPACE: random wall color",
        )
        mlx.mlx_string_put(
            mlx_ptr,
            window,
            20,
            img_h + 30,
            0xFFFFFFFF,
            f"scale={state['scale']} offset=({state['off_x']},{state['off_y']})",
        )

        mlx.mlx_key_hook(window, self._on_key, state)
        mlx.mlx_loop(mlx_ptr)

    # ---------------- layout / autoscale ----------------

    def _compute_layout(self, win_w: int, img_h: int, grid_w: int, grid_h: int) -> Dict[str, int]:
        """
        Compute scale + offsets so the whole maze fits with padding and is centered.
        Each cell is scale x scale pixels.
        """
        usable_w = max(1, win_w - 2 * self._PADDING)
        usable_h = max(1, img_h - 2 * self._PADDING)

        scale_w = usable_w // max(1, grid_w)
        scale_h = usable_h // max(1, grid_h)
        scale = max(self._MIN_SCALE, min(scale_w, scale_h))

        draw_w = grid_w * scale
        draw_h = grid_h * scale

        off_x = self._PADDING + max(0, (usable_w - draw_w) // 2)
        off_y = self._PADDING + max(0, (usable_h - draw_h) // 2)

        return {"scale": scale, "off_x": off_x, "off_y": off_y}

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
        mlx = state["mlx"]
        mlx_ptr = state["mlx_ptr"]
        window = state["window"]

        # ESC
        if keycode == 65307:
            mlx.mlx_destroy_window(mlx_ptr, window)
            mlx.mlx_loop_exit(mlx_ptr)
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
        mlx = state["mlx"]
        mlx_ptr = state["mlx_ptr"]
        window = state["window"]
        image = state["image"]
        image_address = state["image_address"]

        size_line = int(state["size_line"])
        scale = int(state["scale"])
        off_x = int(state["off_x"])
        off_y = int(state["off_y"])

        hex_rows: List[str] = state["hex_rows"]  # type: ignore[assignment]
        entry: Coord = state["entry"]  # type: ignore[assignment]
        exit_: Coord = state["exit"]  # type: ignore[assignment]
        path: List[Coord] = state["path"]  # type: ignore[assignment]
        show_path = bool(state["show_path"])
        wall_color: bytes = state["wall_color"]  # type: ignore[assignment]

        # clear (black)
        image_address[:] = bytes([0, 0, 0, 255]) * (len(image_address) // 4)

        # path (cyan)
        if show_path:
            for px, py in path:
                self._fill_cell(
                    image_address=image_address,
                    scale=scale,
                    size_line=size_line,
                    x=px,
                    y=py,
                    off_x=off_x,
                    off_y=off_y,
                    color=bytes([0, 255, 255, 255]),
                )

        # start (red) / end (green)
        self._fill_cell(image_address, scale, size_line, entry[0], entry[1], off_x, off_y,
                        bytes([255, 0, 0, 255]))
        self._fill_cell(image_address, scale, size_line, exit_[0], exit_[1], off_x, off_y,
                        bytes([0, 255, 0, 255]))

        # forbidden cells (F) - purple
        for row_idx, row in enumerate(hex_rows):
            for col_idx, ch in enumerate(row):
                if ch.upper() == "F":
                    self._fill_cell(image_address, scale, size_line, col_idx, row_idx, off_x, off_y,
                                    bytes([150, 0, 255, 255]))

        # walls from hex
        for row_idx, row in enumerate(hex_rows):
            for col_idx, ch in enumerate(row):
                self._draw_walls(
                    block_hex=ch,
                    row_idx=row_idx,
                    col_idx=col_idx,
                    size_line=size_line,
                    scale=scale,
                    image_address=image_address,
                    color=wall_color,
                    off_x=off_x,
                    off_y=off_y,
                )

        mlx.mlx_put_image_to_window(mlx_ptr, window, image, 0, 0)

    @staticmethod
    def _fill_cell(
        image_address,
        scale: int,
        size_line: int,
        x: int,
        y: int,
        off_x: int,
        off_y: int,
        color: bytes,
    ) -> None:
        """
        Fill a scale x scale block at cell coordinates (x, y) with an offset.
        """
        px = off_x + x * scale
        py = off_y + y * scale

        base_x = px * 4
        base_y = py * size_line

        for i in range(scale):
            start = base_x + base_y + i * size_line
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
        off_x: int,
        off_y: int,
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

        px = off_x + col_idx * scale
        py = off_y + row_idx * scale

        base_x = px * 4
        base_y = py * size_line

        # north
        if has_n:
            image_address[base_x + base_y:base_x + base_y + scale * 4] = color * scale

        # south
        if has_s:
            bottom_y = base_y + (scale - 1) * size_line
            image_address[base_x + bottom_y:base_x + bottom_y + scale * 4] = color * scale

        # west/east
        for i in range(scale):
            line_base = base_y + i * size_line
            if has_w:
                image_address[base_x + line_base:base_x + line_base + 4] = color
            if has_e:
                edge = base_x + line_base + (scale - 1) * 4
                image_address[edge:edge + 4] = color
