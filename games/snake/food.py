"""
Cyber-Grid Snake — Food entity (OOP).
Spawns at random grid positions, avoiding the snake.
Provides a pulsing animation value for the renderer.
"""

import math
import random
import time
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import GRID_WIDTH, GRID_HEIGHT, NEON_MAGENTA

FOOD_COLOR = NEON_MAGENTA


class Food:
    """Single food item on the grid with pulsing animation."""

    def __init__(self, snake_body: list[tuple[int, int]]):
        self.position: tuple[int, int] | None = None
        self._spawn_time = time.time()
        self._spawn(snake_body)

    def _spawn(self, snake_body: list[tuple[int, int]]) -> None:
        """Place food at a random empty cell."""
        empty = [
            (c, r)
            for c in range(GRID_WIDTH)
            for r in range(GRID_HEIGHT)
            if (c, r) not in snake_body
        ]
        if not empty:
            self.position = None
            return
        self.position = random.choice(empty)
        self._spawn_time = time.time()

    def respawn(self, snake_body: list[tuple[int, int]]) -> None:
        """Respawn food after being eaten."""
        self._spawn(snake_body)

    def cell(self) -> tuple[int, int] | None:
        """Return (col, row) of food, or None if no valid spawn."""
        return self.position

    def color(self) -> tuple[int, int, int]:
        """Return draw color for food."""
        return FOOD_COLOR

    def pulse(self) -> float:
        """Return a value from 0.0 to 1.0 based on a sine wave."""
        elapsed = time.time() - self._spawn_time
        return (math.sin(elapsed * 5.0) + 1.0) / 2.0
