"""
Cyber-Grid Snake — Snake entity (OOP).
Manages body segments, direction queue, movement, and collision logic.
"""

from collections import deque
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import (
    GRID_WIDTH,
    GRID_HEIGHT,
    NEON_CYAN,
    NEON_GREEN,
)

INITIAL_SNAKE_LENGTH = 3
SNAKE_HEAD_COLOR = NEON_CYAN
SNAKE_BODY_COLOR = NEON_GREEN

# Map each direction to the one that would reverse it
_OPPOSITE = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}


class Snake:
    """Represents the player-controlled snake on the grid."""

    # Direction deltas (col, row); grid is (x, y) with (0,0) top-left
    DIRECTIONS = {
        "UP": (0, -1),
        "DOWN": (0, 1),
        "LEFT": (-1, 0),
        "RIGHT": (1, 0),
    }

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        """Reset snake to initial state (center, heading right)."""
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2
        self.body = []
        for i in range(INITIAL_SNAKE_LENGTH):
            self.body.append((center_x - i, center_y))
        self.direction = "RIGHT"
        self.grow_pending = 0
        # Input queue — buffers up to 2 queued turns so rapid key
        # presses (e.g. RIGHT→DOWN→LEFT in one frame) are processed
        # one per tick instead of all at once, preventing accidental
        # self-collision.
        self._turn_queue: deque[str] = deque(maxlen=2)

    def head(self) -> tuple[int, int]:
        """Return (col, row) of the head."""
        return self.body[0]

    def set_direction(self, new_direction: str) -> None:
        """Queue a direction change (rejects reversals)."""
        if new_direction not in self.DIRECTIONS:
            return
        ref = self._turn_queue[-1] if self._turn_queue else self.direction
        if new_direction != _OPPOSITE.get(ref) and new_direction != ref:
            self._turn_queue.append(new_direction)

    def move(self) -> tuple[int, int] | None:
        """Advance snake by one cell. Returns new head or None if dead."""
        if self._turn_queue:
            queued = self._turn_queue.popleft()
            if queued != _OPPOSITE.get(self.direction):
                self.direction = queued

        dx, dy = self.DIRECTIONS[self.direction]
        head_col, head_row = self.head()
        new_head = (head_col + dx, head_row + dy)

        if not (0 <= new_head[0] < GRID_WIDTH and 1 <= new_head[1] < GRID_HEIGHT):
            return None

        body_without_tail = self.body[:-1] if self.grow_pending <= 0 else self.body
        if new_head in body_without_tail:
            return None

        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
        return new_head

    def grow(self, amount: int = 1) -> None:
        """Schedule growth over the next `amount` moves."""
        self.grow_pending += amount

    def contains(self, cell: tuple[int, int]) -> bool:
        """Return True if cell is part of the snake."""
        return cell in self.body

    def segments_with_colors(self) -> list[tuple[tuple[int, int], tuple[int, int, int]]]:
        """Return [(cell, color), ...] for head then body (for drawing)."""
        result = []
        for i, cell in enumerate(self.body):
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
            result.append((cell, color))
        return result
