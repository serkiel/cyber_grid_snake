"""
Cyber Dash — Main game loop (Geometry Dash-like runner).
Auto-scrolling platformer where the player jumps over obstacles.

States
------
TITLE     – Start screen; press SPACE to begin.
PLAYING   – Active gameplay; SPACE/UP to jump, ESC to menu.
GAME_OVER – Show score; SPACE to retry, ESC to menu.
"""

import pygame
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import SCREEN_WIDTH, SCREEN_HEIGHT

from games.cyber_dash.player import Player
from games.cyber_dash.obstacles import ObstacleManager
from games.cyber_dash.renderer import DashRenderer

# Game states
STATE_TITLE = "TITLE"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"

# Target distance for 100% progress (pixels)
LEVEL_LENGTH = 15000

FPS = 60


class DashGame:
    """Main controller for the Cyber Dash game."""

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        self.screen = screen
        self.clock = clock
        self.renderer = DashRenderer(self.screen)
        self.player = Player()
        self.obstacles = ObstacleManager()
        self.state = STATE_TITLE
        self.running = True
        self.return_to_menu = False
        self.score = 0       # progress percentage
        self.high_score = 0
        self.attempt = 1
        self.distance = 0.0  # total pixels traveled
        self._tick = 0
        self._death_timer = 0  # delay before showing game over

    # ── Event handling ──────────────────────────────────────

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type != pygame.KEYDOWN:
                continue

            key = event.key

            if key == pygame.K_ESCAPE:
                self.return_to_menu = True
                self.running = False
                return

            if self.state == STATE_TITLE:
                if key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w,
                           pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._start_game()
                continue

            if self.state == STATE_PLAYING:
                if key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    self.player.jump()
                continue

            if self.state == STATE_GAME_OVER:
                if key == pygame.K_SPACE:
                    self._restart()

        # Also check for held keys for continuous jump feel
        if self.state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            # Jump is handled on KEYDOWN only (no holding)

    # ── State transitions ───────────────────────────────────

    def _start_game(self) -> None:
        """Start a new game from the title screen."""
        self.player.reset()
        self.obstacles.reset()
        self.distance = 0.0
        self.score = 0
        self.attempt = 1
        self.state = STATE_PLAYING

    def _restart(self) -> None:
        """Restart after death."""
        self.player.reset()
        self.obstacles.reset()
        self.distance = 0.0
        self.score = 0
        self.attempt += 1
        self.state = STATE_PLAYING
        self._death_timer = 0

    # ── Update ──────────────────────────────────────────────

    def _update(self) -> None:
        if self.state != STATE_PLAYING:
            return

        if not self.player.alive:
            self._death_timer += 1
            if self._death_timer > 30:  # half-second delay at 60fps
                if self.score > self.high_score:
                    self.high_score = self.score
                self.state = STATE_GAME_OVER
            return

        speed = self.obstacles.scroll_speed

        # Update obstacles
        self.obstacles.update(speed)
        self.obstacles.increase_speed()

        # Update player with platform info
        platforms_data = self.obstacles.get_platforms()
        self.player.update(platforms_data)

        # Track distance and score
        self.distance += speed
        self.score = min(100, int((self.distance / LEVEL_LENGTH) * 100))

        # Check if level completed
        if self.score >= 100:
            if self.score > self.high_score:
                self.high_score = self.score
            self.state = STATE_GAME_OVER
            return

        # Collision detection
        self._check_collisions()

    def _check_collisions(self) -> None:
        """Check player against obstacles."""
        px, py, pw, ph = self.player.get_rect()
        player_rect = pygame.Rect(px, py, pw, ph)

        # Check spikes
        for spike in self.obstacles.get_spikes():
            # Simplified triangle collision — use bounding box with slight shrink
            spike_rect = pygame.Rect(
                spike['x'] + 5, spike['y'] + 8,
                spike['w'] - 10, spike['h'] - 8
            )
            if player_rect.colliderect(spike_rect):
                self.player.alive = False
                self._death_timer = 0
                return

        # Check blocks
        for block in self.obstacles.get_blocks():
            block_rect = pygame.Rect(block['x'], block['y'], block['w'], block['h'])
            if player_rect.colliderect(block_rect):
                # Check if landing on top (could be a platform-like landing)
                if (self.player.vy >= 0 and
                    py + ph <= block['y'] + 10 and
                    py + ph >= block['y'] - 5):
                    # Land on block
                    self.player.y = block['y'] - self.player.SIZE
                    self.player.vy = 0
                    self.player.on_ground = True
                else:
                    self.player.alive = False
                    self._death_timer = 0
                    return

        # Check gaps (player falls through if they're over a gap)
        for gap in self.obstacles.get_gaps():
            gap_rect = pygame.Rect(gap['x'], gap['y'], gap['w'], gap['h'])
            # If player center is over the gap and they're at ground level
            player_cx = px + pw // 2
            if (gap['x'] < player_cx < gap['x'] + gap['w'] and
                py + ph >= gap['y'] - 5 and
                self.player.on_ground):
                # Player falls into gap
                self.player.on_ground = False
                self.player.vy = 2  # start falling

    # ── Draw ────────────────────────────────────────────────

    def _draw(self) -> None:
        self._tick += 1

        if self.state == STATE_TITLE:
            self.renderer.draw_title_screen(self._tick)
            pygame.display.flip()
            return

        # Playing or Game Over
        speed = self.obstacles.scroll_speed if self.state == STATE_PLAYING else 0
        self.renderer.draw_background(speed)
        self.renderer.draw_ground(self.obstacles.get_gaps())
        self.renderer.draw_obstacles(self.obstacles.obstacles, self._tick)
        self.renderer.draw_player(self.player, self._tick)
        self.renderer.draw_hud(self.score, self.high_score, self.attempt)
        self.renderer.draw_progress_bar(self.distance / LEVEL_LENGTH)

        if self.state == STATE_GAME_OVER:
            self.renderer.draw_game_over(self.score, self.high_score, self.attempt)

        pygame.display.flip()

    # ── Main loop ───────────────────────────────────────────

    def run(self) -> bool:
        """Main game loop. Returns True to return to menu, False to quit."""
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)
        return self.return_to_menu
