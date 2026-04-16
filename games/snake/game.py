"""
Cyber-Grid Snake — Main game loop and state (OOP).
Orchestrates Snake, Food, SnakeRenderer, input, and win/lose conditions.

States
------
TITLE     – Start screen; press ENTER to begin.
PLAYING   – Active gameplay; P to pause, ESC to quit.
PAUSED    – Frozen; press P to resume.
GAME_OVER – Show score; press SPACE to restart.
"""

import pygame
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)

START_FPS = 10
FPS_INCREMENT = 0.5
MAX_FPS = 25

from games.snake.snake import Snake
from games.snake.food import Food
from games.snake.renderer import SnakeRenderer

# Game states
STATE_TITLE = "TITLE"
STATE_PLAYING = "PLAYING"
STATE_PAUSED = "PAUSED"
STATE_GAME_OVER = "GAME_OVER"

# Key-to-direction mapping (arrow keys + WASD)
_KEY_DIR = {
    pygame.K_UP: "UP",       pygame.K_w: "UP",
    pygame.K_DOWN: "DOWN",   pygame.K_s: "DOWN",
    pygame.K_LEFT: "LEFT",   pygame.K_a: "LEFT",
    pygame.K_RIGHT: "RIGHT", pygame.K_d: "RIGHT",
}


class SnakeGame:
    """Main game controller: init, input, update, draw, and run loop."""

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        self.screen = screen
        self.clock = clock
        self.renderer = SnakeRenderer(self.screen)
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.score = 0
        self.high_score = 0
        self.current_fps = START_FPS
        self.running = True
        self.return_to_menu = False
        self.state = STATE_TITLE
        self._tick = 0

        try:
            self.sfx_eat = pygame.mixer.Sound("eat.wav")
        except:
            self.sfx_eat = None

    # ── Event handling ──────────────────────────────────────────

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type != pygame.KEYDOWN:
                continue

            key = event.key

            if key == pygame.K_ESCAPE:
                if self.state not in (STATE_GAME_OVER,):
                    self.return_to_menu = True
                    self.running = False
                    return

            if self.state == STATE_TITLE:
                if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._start_game()
                continue

            if self.state == STATE_PLAYING:
                if key == pygame.K_p:
                    self.state = STATE_PAUSED
                    continue
                direction = _KEY_DIR.get(key)
                if direction:
                    self.snake.set_direction(direction)
                continue

            if self.state == STATE_PAUSED:
                if key == pygame.K_p:
                    self.state = STATE_PLAYING
                continue

            if self.state == STATE_GAME_OVER:
                if key == pygame.K_SPACE:
                    self._restart()
                elif key == pygame.K_ESCAPE:
                    self.return_to_menu = True
                    self.running = False
                    return

    def _start_game(self) -> None:
        self.snake.reset()
        self.food = Food(self.snake.body)
        self.score = 0
        self.current_fps = START_FPS
        self.state = STATE_PLAYING

    def _restart(self) -> None:
        self.snake.reset()
        self.food = Food(self.snake.body)
        self.score = 0
        self.current_fps = START_FPS
        self.state = STATE_PLAYING

    def _update(self) -> None:
        if self.state != STATE_PLAYING:
            return

        new_head = self.snake.move()
        if new_head is None:
            if self.score > self.high_score:
                self.high_score = self.score
            self.state = STATE_GAME_OVER
            return

        if self.food.cell() and new_head == self.food.cell():
            if getattr(self, 'sfx_eat', None): self.sfx_eat.play()
            self.snake.grow(1)
            self.score += 1
            self.current_fps = min(self.current_fps + FPS_INCREMENT, MAX_FPS)
            self.food.respawn(self.snake.body)

    def _draw(self) -> None:
        self._tick += 1

        if self.state == STATE_TITLE:
            self.renderer.draw_title_screen(self._tick)
            pygame.display.flip()
            return

        self.renderer.clear()
        self.renderer.draw_grid()
        self.renderer.draw_snake(self.snake.segments_with_colors())

        if self.food.cell():
            self.renderer.draw_food(
                self.food.cell()[0],
                self.food.cell()[1],
                self.food.color(),
                self.food.pulse(),
            )

        self.renderer.draw_hud(self.score, self.high_score)

        if self.state == STATE_PAUSED:
            self.renderer.draw_pause_overlay()

        if self.state == STATE_GAME_OVER:
            self.renderer.draw_game_over(self.score, self.high_score, self._tick)

        pygame.display.flip()

    def run(self) -> bool:
        """Main game loop. Returns True if should return to menu, False to quit."""
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(self.current_fps)
        return self.return_to_menu
