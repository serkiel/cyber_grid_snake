"""
Cyber-Grid Snake — Main game loop and state (OOP).
Orchestrates Snake, Food, GridRenderer, input, and win/lose conditions.

States
------
TITLE     – Start screen; press ENTER to begin.
PLAYING   – Active gameplay; P to pause, ESC to quit.
PAUSED    – Frozen; press P to resume.
GAME_OVER – Show score; press SPACE to restart.
"""

import pygame
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    START_FPS,
    FPS_INCREMENT,
    MAX_FPS,
)
from snake import Snake
from food import Food
from grid_renderer import GridRenderer

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


class Game:
    """Main game controller: init, input, update, draw, and run loop."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.SCALED)
        pygame.display.set_caption("Cyber-Grid Snake")
        self.clock = pygame.time.Clock()
        self.renderer = GridRenderer(self.screen)
        self.snake = Snake()
        self.food = Food(self.snake.body)
        self.score = 0
        self.high_score = 0
        self.current_fps = START_FPS
        self.running = True
        self.state = STATE_TITLE
        self._tick = 0  # frame counter for title animation

    # ── Event handling ──────────────────────────────────────────

    def _handle_events(self) -> None:
        """Process pygame events (quit, arrow keys, WASD, P, ESC, ENTER, SPACE)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type != pygame.KEYDOWN:
                continue

            key = event.key

            if key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
                continue
                
            # ESC quits from any state
            if key == pygame.K_ESCAPE:
                self.running = False
                return

            # ── Title screen ─────────────────────────────────
            if self.state == STATE_TITLE:
                if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._start_game()
                continue

            # ── Playing ──────────────────────────────────────
            if self.state == STATE_PLAYING:
                if key == pygame.K_p:
                    self.state = STATE_PAUSED
                    continue
                direction = _KEY_DIR.get(key)
                if direction:
                    self.snake.set_direction(direction)
                continue

            # ── Paused ───────────────────────────────────────
            if self.state == STATE_PAUSED:
                if key == pygame.K_p:
                    self.state = STATE_PLAYING
                continue

            # ── Game over ────────────────────────────────────
            if self.state == STATE_GAME_OVER:
                if key == pygame.K_SPACE:
                    self._restart()

    # ── State transitions ───────────────────────────────────────

    def _start_game(self) -> None:
        """Transition from title screen to gameplay."""
        self.snake.reset()
        self.food = Food(self.snake.body)
        self.score = 0
        self.current_fps = START_FPS
        self.state = STATE_PLAYING

    def _restart(self) -> None:
        """Reset game state for a new round (keeps high score)."""
        self.snake.reset()
        self.food = Food(self.snake.body)
        self.score = 0
        self.current_fps = START_FPS
        self.state = STATE_PLAYING

    # ── Update ──────────────────────────────────────────────────

    def _update(self) -> None:
        """One tick: move snake, check food, check death."""
        if self.state != STATE_PLAYING:
            return

        new_head = self.snake.move()
        if new_head is None:
            # Snake died — update high score
            if self.score > self.high_score:
                self.high_score = self.score
            self.state = STATE_GAME_OVER
            return

        if self.food.cell() and new_head == self.food.cell():
            self.snake.grow(1)
            self.score += 1
            self.current_fps = min(self.current_fps + FPS_INCREMENT, MAX_FPS)
            self.food.respawn(self.snake.body)

    # ── Draw ────────────────────────────────────────────────────

    def _draw(self) -> None:
        """Render the current state to the screen."""
        self._tick += 1

        # Title screen
        if self.state == STATE_TITLE:
            self.renderer.draw_title_screen(self._tick)
            pygame.display.flip()
            return

        # Playing / Paused / Game Over — all share the same base scene
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
            self.renderer.draw_game_over(self.score, self.high_score)

        pygame.display.flip()

    # ── Main loop ───────────────────────────────────────────────

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(self.current_fps)
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
