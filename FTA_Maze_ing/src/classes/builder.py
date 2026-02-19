from .grid import Grid
import random


class OriginShift:
    def __init__(self, grid: Grid) -> None:
        self.grid = grid
        self.origin = None
        self.deltas = {
            "north": (0, -1),
            "south": (0, 1),
            "east": (1, 0),
            "west": (-1, 0)
        }
        self.opposites = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }

    def init_vectors(self):
        w, h = self.grid.grid_width, self.grid.grid_height

        for row in self.grid.matrix:
            for cell in row:
                cell.paths = {k: False for k in cell.paths}
                cell.vector = None

        sx = (w - 7) // 2
        sy = (h - 5) // 2
        overrides = {
            # Внутри "4" (чаша) -> Вверх
            (1, 0): "north", (1, 1): "north",
            # Разрыв между "4" и "2" -> Вниз (Коллектор)
            (3, 0): "south", (3, 1): "south",
            (3, 2): "south", (3, 3): "south", (3, 4): "south",
            # Внутри "2" -> Влево
            (4, 1): "west", (5, 1): "west",
            # Низ "4" -> Вниз
            (0, 3): "south", (1, 3): "south", (0, 4): "south", (1, 4): "south",
            # Хвост "2" -> Вниз
            (5, 3): "south", (6, 3): "south"
        }

        # 4. Главный проход по сетке
        for y in range(h):
            for x in range(w):
                cell = self.grid.matrix[y][x]

                if cell.forbidden:
                    continue

                # ВАЖНО: Правый нижний угол — это Сток (Origin)
                if x == w - 1 and y == h - 1:
                    self.origin = cell
                    cell.vector = None
                    continue

                direction = None

                rel_pos = (x - sx, y - sy)
                if rel_pos in overrides:
                    desired = overrides[rel_pos]
                    if self._is_valid_move(x, y, desired):
                        direction = desired

                if not direction:
                    if self._is_valid_move(x, y, "east"):
                        direction = "east"
                    elif self._is_valid_move(x, y, "south"):
                        direction = "south"
                    elif self._is_valid_move(x, y, "north"):
                        direction = "north"
                    elif self._is_valid_move(x, y, "west"):
                        direction = "west"

                if direction:
                    self._set_vector(cell, direction)
                else:
                    self.origin = cell
                    cell.vector = None

    def _set_vector(self, cell, direction: str):
        """
        Устанавливает вектор логически И открывает стены графически.
        """
        cell.vector = direction

        cell.paths[direction] = True

        dx, dy = self.deltas[direction]
        neighbor = self.grid.matrix[cell.cell_y + dy][cell.cell_x + dx]

        opposite_dir = self.opposites[direction]
        neighbor.paths[opposite_dir] = True

    def _is_valid_move(self, x, y, direction) -> bool:
        """Проверка: можно ли из (x,y) шагнуть в direction?"""
        dx, dy = self.deltas[direction]
        nx, ny = x + dx, y + dy
        if not (0 <= nx < self.grid.grid_width and
                0 <= ny < self.grid.grid_height):
            return False
        if self.grid.matrix[ny][nx].forbidden:
            return False
        return True

    def _close_wall(self, cell, direction: str):
        """
        Физически закрывает стену (paths=False) между клеткой и соседом.
        Используется перед тем, как изменить вектор клетки.
        """
        cell.paths[direction] = False

        dx, dy = self.deltas[direction]
        neighbor = self.grid.matrix[cell.cell_y + dy][cell.cell_x + dx]

        opposite_dir = self.opposites[direction]
        neighbor.paths[opposite_dir] = False

    def _get_valid_neighbors(self, cell):
        """Возвращает список (Cell, direction), к которым можно прокопаться"""
        candidates = []

        for direction, (dx, dy) in self.deltas.items():
            nx, ny = cell.cell_x + dx, cell.cell_y + dy
            if (0 <= nx < self.grid.grid_width and
                    0 <= ny < self.grid.grid_height):
                neighbor = self.grid.matrix[ny][nx]
                if not neighbor.forbidden:
                    candidates.append((neighbor, direction))
        return candidates

    def step(self) -> list:
        updates = []

        current_origin = self.origin
        neighbors = self._get_valid_neighbors(current_origin)
        if not neighbors:
            return []

        target, direction = random.choice(neighbors)

        current_origin.visited = True
        target.visited = True

        if target.vector:
            dx, dy = self.deltas[target.vector]
            old_neighbor = (
                self.grid.matrix)[target.cell_y + dy][target.cell_x + dx]
            self._close_wall(target, target.vector)
            updates.append(old_neighbor)

        self._set_vector(current_origin, direction)
        target.vector = None
        self.origin = target

        updates.append(current_origin)
        updates.append(target)

        return updates
