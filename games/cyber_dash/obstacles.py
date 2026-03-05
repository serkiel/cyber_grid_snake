"""
Cyber Dash — Obstacle generation and management.
Creates spikes, blocks, gaps, and platforms that scroll from right to left.
"""

import random
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import SCREEN_WIDTH, SCREEN_HEIGHT


# Ground level — must match player.py
GROUND_Y = SCREEN_HEIGHT - 80


class ObstacleManager:
    """Spawns, updates, and provides obstacle data for the Cyber Dash game."""

    # Obstacle types
    SPIKE = "spike"
    BLOCK = "block"
    GAP = "gap"
    PLATFORM = "platform"

    # Minimum gap between any two obstacles (pixels)
    MIN_SPACING = 250
    MAX_SPACING = 500

    def __init__(self):
        self.obstacles: list[dict] = []
        self.scroll_speed = 5.0
        self.distance_since_last = 0.0
        self.next_spawn_dist = 300  # first obstacle appears after 300px
        self._pattern_index = 0
        # Pre-defined patterns for variety
        self._patterns = [
            [self.SPIKE],
            [self.SPIKE, self.SPIKE],
            [self.BLOCK],
            [self.GAP],
            [self.SPIKE, self.BLOCK],
            [self.PLATFORM, self.SPIKE],
            [self.GAP, self.PLATFORM],
            [self.BLOCK, self.SPIKE, self.SPIKE],
            [self.BLOCK, self.GAP],
        ]

    def reset(self) -> None:
        """Clear all obstacles and reset state."""
        self.obstacles.clear()
        self.scroll_speed = 5.0
        self.distance_since_last = 0.0
        self.next_spawn_dist = 300
        self._pattern_index = 0

    def _create_obstacle(self, obs_type: str, x: float) -> dict:
        """Create a single obstacle dict at position x."""
        if obs_type == self.SPIKE:
            w = 30
            h = 40
            return {
                'type': self.SPIKE,
                'x': x, 'y': GROUND_Y - h,
                'w': w, 'h': h,
            }
        elif obs_type == self.BLOCK:
            w = 40
            h = random.choice([40, 60, 80])
            return {
                'type': self.BLOCK,
                'x': x, 'y': GROUND_Y - h,
                'w': w, 'h': h,
            }
        elif obs_type == self.GAP:
            w = random.randint(80, 140)
            return {
                'type': self.GAP,
                'x': x, 'y': GROUND_Y,
                'w': w, 'h': 80,  # depth of pit
            }
        elif obs_type == self.PLATFORM:
            w = random.randint(80, 150)
            h = 12
            plat_y = GROUND_Y - random.randint(80, 130)
            return {
                'type': self.PLATFORM,
                'x': x, 'y': plat_y,
                'w': w, 'h': h,
            }
        return {'type': obs_type, 'x': x, 'y': GROUND_Y, 'w': 30, 'h': 30}

    def update(self, dt_pixels: float) -> None:
        """Move all obstacles left and spawn new ones."""
        # Move obstacles
        for obs in self.obstacles:
            obs['x'] -= dt_pixels

        # Remove off-screen obstacles
        self.obstacles = [o for o in self.obstacles if o['x'] + o['w'] > -50]

        # Spawn new obstacles
        self.distance_since_last += dt_pixels
        if self.distance_since_last >= self.next_spawn_dist:
            self._spawn_pattern()
            self.distance_since_last = 0
            # Gradually decrease spacing (harder over time)
            spacing = max(180, self.MAX_SPACING - int(self.scroll_speed * 8))
            self.next_spawn_dist = random.randint(self.MIN_SPACING - 50, spacing)

    def _spawn_pattern(self) -> None:
        """Spawn a pattern of obstacles from the right edge."""
        pattern = self._patterns[self._pattern_index % len(self._patterns)]
        self._pattern_index += 1
        # Mix in some randomness
        if random.random() < 0.3:
            pattern = random.choice(self._patterns)

        x = SCREEN_WIDTH + 20
        for obs_type in pattern:
            obs = self._create_obstacle(obs_type, x)
            self.obstacles.append(obs)
            x += obs['w'] + random.randint(60, 120)

    def get_spikes(self) -> list[dict]:
        """Return all spike obstacles (for collision)."""
        return [o for o in self.obstacles if o['type'] == self.SPIKE]

    def get_blocks(self) -> list[dict]:
        """Return all block obstacles (for collision)."""
        return [o for o in self.obstacles if o['type'] == self.BLOCK]

    def get_gaps(self) -> list[dict]:
        """Return all gap obstacles (for collision)."""
        return [o for o in self.obstacles if o['type'] == self.GAP]

    def get_platforms(self) -> list[dict]:
        """Return all platform obstacles (for landing)."""
        return [o for o in self.obstacles if o['type'] == self.PLATFORM]

    def increase_speed(self, amount: float = 0.002) -> None:
        """Gradually increase scroll speed."""
        self.scroll_speed = min(self.scroll_speed + amount, 14.0)
