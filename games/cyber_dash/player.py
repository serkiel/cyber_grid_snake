"""
Cyber Dash — Player entity.
A cube character that jumps with gravity-based physics.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import SCREEN_HEIGHT, NEON_CYAN


class Player:
    """The player cube that jumps over obstacles."""

    SIZE = 40             # pixel size of the cube
    GROUND_Y = SCREEN_HEIGHT - 80  # ground level (bottom of player)
    GRAVITY = 0.8
    JUMP_VELOCITY = -14
    MAX_FALL_SPEED = 18

    def __init__(self):
        self.x = 100
        self.y = self.GROUND_Y - self.SIZE
        self.vy = 0.0
        self.on_ground = True
        self.alive = True
        self.rotation = 0.0  # visual rotation in degrees

    def reset(self) -> None:
        """Reset player to starting position."""
        self.x = 100
        self.y = self.GROUND_Y - self.SIZE
        self.vy = 0.0
        self.on_ground = True
        self.alive = True
        self.rotation = 0.0

    def jump(self) -> None:
        """Initiate a jump if on the ground."""
        if self.on_ground and self.alive:
            self.vy = self.JUMP_VELOCITY
            self.on_ground = False

    def update(self, platforms: list = None) -> None:
        """Apply gravity and update position."""
        if not self.alive:
            return

        # Apply gravity
        self.vy += self.GRAVITY
        if self.vy > self.MAX_FALL_SPEED:
            self.vy = self.MAX_FALL_SPEED

        self.y += self.vy

        # Check platform collisions (land on top of platforms)
        landed = False
        if platforms:
            for plat in platforms:
                # Only land if falling down onto platform
                if (self.vy >= 0 and
                    self.x + self.SIZE > plat['x'] and
                    self.x < plat['x'] + plat['w'] and
                    self.y + self.SIZE >= plat['y'] and
                    self.y + self.SIZE <= plat['y'] + 15):
                    self.y = plat['y'] - self.SIZE
                    self.vy = 0
                    self.on_ground = True
                    landed = True
                    break

        # Ground collision
        if self.y + self.SIZE >= self.GROUND_Y and not landed:
            self.y = self.GROUND_Y - self.SIZE
            self.vy = 0
            self.on_ground = True

        # Fell off screen (into a gap)
        if self.y > SCREEN_HEIGHT + 50:
            self.alive = False

        # Visual rotation while airborne
        if not self.on_ground:
            self.rotation += 5
        else:
            # Snap rotation to nearest 90
            self.rotation = round(self.rotation / 90) * 90

    def get_rect(self) -> tuple:
        """Return (x, y, w, h) for collision detection."""
        margin = 4  # slight inset for forgiving collision
        return (self.x + margin, self.y + margin,
                self.SIZE - 2 * margin, self.SIZE - 2 * margin)
