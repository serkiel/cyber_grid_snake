import pygame
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BG_DARK, NEON_PINK, NEON_CYAN, NEON_GREEN, NEON_YELLOW, NEON_MAGENTA

STATE_TITLE    = "TITLE"
STATE_PLAYING  = "PLAYING"
STATE_PAUSED   = "PAUSED"
STATE_GAME_OVER = "GAME_OVER"
STATE_VICTORY  = "VICTORY"

FPS = 60
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2


class Paddle:
    def __init__(self):
        self.width  = 110
        self.height = 14
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = SCREEN_HEIGHT - 44
        self.speed = 10
        self.color = NEON_PINK

    def move_left(self):
        self.x = max(0, self.x - self.speed)

    def move_right(self):
        self.x = min(SCREEN_WIDTH - self.width, self.x + self.speed)

    def draw(self, surface):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        # Glow
        glow = pygame.Surface((self.width + 16, self.height + 16), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*self.color, 45), glow.get_rect(), border_radius=6)
        surface.blit(glow, (self.x - 8, self.y - 8))
        # Body
        pygame.draw.rect(surface, self.color, rect, border_radius=4)
        # Bright centre stripe
        pygame.draw.rect(surface, (255, 200, 230),
                         pygame.Rect(self.x + self.width // 2 - 1, self.y + 3, 2, self.height - 6))


class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.dx = 5
        self.dy = -5
        self.speed_multiplier = 1.0
        self.color = NEON_CYAN
        self.trail: list[tuple[float, float]] = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)

        self.x += self.dx * self.speed_multiplier
        self.y += self.dy * self.speed_multiplier

        if self.x - self.radius <= 0:
            self.dx = abs(self.dx)
            self.x = self.radius
        elif self.x + self.radius >= SCREEN_WIDTH:
            self.dx = -abs(self.dx)
            self.x = SCREEN_WIDTH - self.radius

        if self.y - self.radius <= 0:
            self.dy = abs(self.dy)
            self.y = self.radius

    def draw(self, surface):
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(100 * (i / max(len(self.trail), 1)))
            r = max(1, int(self.radius * 0.6 * (i / max(len(self.trail), 1))))
            ts = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            pygame.draw.circle(ts, (*self.color, alpha), (r * 2, r * 2), r * 2)
            surface.blit(ts, (int(tx) - r * 2, int(ty) - r * 2))
        # Glow
        glow = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 70), (self.radius * 2, self.radius * 2), self.radius * 2)
        surface.blit(glow, (int(self.x) - self.radius * 2, int(self.y) - self.radius * 2))
        # Core
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius // 2)


class Block:
    def __init__(self, x, y, width, height, color, strength=1):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.strength = strength

    def draw(self, surface):
        # Glow layer
        glow = pygame.Surface((self.rect.width + 6, self.rect.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*self.color, 35), glow.get_rect(), border_radius=3)
        surface.blit(glow, (self.rect.x - 3, self.rect.y - 3))
        # Block body
        pygame.draw.rect(surface, self.color, self.rect, border_radius=2)
        # White top-edge shine
        pygame.draw.line(surface, (255, 255, 255),
                         (self.rect.x + 2, self.rect.y + 1),
                         (self.rect.right - 2, self.rect.y + 1), 1)


class BreakoutGame:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock  = clock
        self.running = True
        self.return_to_menu = False
        self.state = STATE_TITLE

        self.font_xl = pygame.font.Font(None, 82)
        self.font_lg = pygame.font.Font(None, 60)
        self.font_md = pygame.font.Font(None, 44)
        self.font_sm = pygame.font.Font(None, 30)
        self.font_hud = pygame.font.Font(None, 26)

        self._tick   = 0
        self._bg_offset = 0.0

        self.reset_game()

    # ── Reset ─────────────────────────────────────────────────────
    def reset_game(self):
        self.paddle = Paddle()
        self.ball   = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 65)
        self.blocks = []
        self.score  = 0
        self.lives  = 3
        self.level  = 1
        self.create_blocks()

    def create_blocks(self):
        self.blocks.clear()
        rows = 4 + self.level
        cols = 10
        block_width  = (SCREEN_WIDTH - 80) // cols
        block_height = 22

        colors = [NEON_PINK, NEON_CYAN, NEON_GREEN, NEON_YELLOW, NEON_MAGENTA]

        for row in range(rows):
            for col in range(cols):
                x = 40 + col * block_width
                y = 75 + row * (block_height + 5)
                color = colors[row % len(colors)]
                self.blocks.append(Block(x, y, block_width - 3, block_height, color))

    # ── Events ────────────────────────────────────────────────────
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                    else:
                        self.return_to_menu = True
                        self.running = False
                    return

                if self.state == STATE_TITLE:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.state = STATE_PLAYING

                elif self.state == STATE_PAUSED:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_p):
                        self.state = STATE_PLAYING

                elif self.state in (STATE_GAME_OVER, STATE_VICTORY):
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.reset_game()
                        self.state = STATE_PLAYING

    # ── Update ────────────────────────────────────────────────────
    def update(self):
        if self.state != STATE_PLAYING:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move_right()

        self.ball.update()

        # Paddle collision
        paddle_rect = pygame.Rect(self.paddle.x, self.paddle.y,
                                  self.paddle.width, self.paddle.height)
        ball_rect = pygame.Rect(self.ball.x - self.ball.radius,
                                self.ball.y - self.ball.radius,
                                self.ball.radius * 2, self.ball.radius * 2)

        if ball_rect.colliderect(paddle_rect) and self.ball.dy > 0:
            self.ball.dy = -self.ball.dy
            hit_pos = (self.ball.x - self.paddle.x) / self.paddle.width
            self.ball.dx = 10 * (hit_pos - 0.5)
            self.ball.speed_multiplier = min(1.6, self.ball.speed_multiplier + 0.02)

        # Block collision
        for block in self.blocks[:]:
            if ball_rect.colliderect(block.rect):
                self.blocks.remove(block)
                self.score += 10 * self.level
                self.ball.dy = -self.ball.dy
                break

        # Lost ball
        if self.ball.y + self.ball.radius >= SCREEN_HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.state = STATE_GAME_OVER
            else:
                self.ball   = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 65)
                self.paddle = Paddle()

        # Level complete
        if len(self.blocks) == 0:
            self.level += 1
            if self.level > 5:
                self.state = STATE_VICTORY
            else:
                self.ball   = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 65)
                self.paddle = Paddle()
                self.create_blocks()

    # ── Drawing helpers ───────────────────────────────────────────
    def _draw_text(self, text, font, color, cx, cy):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(cx, cy))
        self.screen.blit(surf, rect)

    def _draw_bg(self):
        self.screen.fill(BG_DARK)
        self._bg_offset = (self._bg_offset + 0.4) % 40
        for x in range(-40, SCREEN_WIDTH + 40, 40):
            sx = x - int(self._bg_offset)
            pygame.draw.line(self.screen, (14, 18, 28), (sx, 0), (sx, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (14, 18, 28), (0, y), (SCREEN_WIDTH, y), 1)

    def _draw_overlay(self, title, color, hint):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        box_w, box_h = 480, 190
        box_x = CENTER_X - box_w // 2
        box_y = CENTER_Y - box_h // 2

        # Glow box
        glow_surf = pygame.Surface((box_w + 16, box_h + 16), pygame.SRCALPHA)
        glow_surf.fill((*color, 20))
        self.screen.blit(glow_surf, (box_x - 8, box_y - 8))

        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((6, 8, 18, 220))
        self.screen.blit(box_surf, (box_x, box_y))
        pygame.draw.rect(self.screen, color, (box_x, box_y, box_w, box_h), 2, border_radius=6)

        self._draw_text(title, self.font_lg, color, CENTER_X, box_y + 52)
        self._draw_text(f"SCORE: {self.score}", self.font_md, NEON_CYAN, CENTER_X, box_y + 110)

        # Pulsing hint
        alpha = int(140 + 115 * ((math.sin(self._tick * 0.09) + 1) / 2))
        hint_surf = self.font_sm.render(hint, True, (150, 155, 180))
        hint_surf.set_alpha(alpha)
        hint_rect = hint_surf.get_rect(center=(CENTER_X, box_y + 160))
        self.screen.blit(hint_surf, hint_rect)

    def _draw_hud(self):
        """Styled top HUD bar."""
        bar_h = 30
        bar = pygame.Surface((SCREEN_WIDTH, bar_h))
        bar.set_alpha(180)
        bar.fill((8, 10, 20))
        self.screen.blit(bar, (0, 0))
        glow_line = pygame.Surface((SCREEN_WIDTH, 2))
        glow_line.set_alpha(55)
        glow_line.fill(NEON_PINK)
        self.screen.blit(glow_line, (0, bar_h))
        pygame.draw.line(self.screen, NEON_PINK, (0, bar_h), (SCREEN_WIDTH, bar_h), 1)

        # Score
        s_label = self.font_hud.render("SCORE", True, (70, 75, 100))
        s_val   = self.font_hud.render(str(self.score), True, NEON_CYAN)
        self.screen.blit(s_label, (14, 5))
        self.screen.blit(s_val,   (14 + s_label.get_width() + 6, 5))

        # Level
        lv_label = self.font_hud.render("LEVEL", True, (70, 75, 100))
        lv_val   = self.font_hud.render(str(self.level), True, NEON_YELLOW)
        lv_total = lv_label.get_width() + 6 + lv_val.get_width()
        self.screen.blit(lv_label, (CENTER_X - lv_total // 2, 5))
        self.screen.blit(lv_val,   (CENTER_X - lv_total // 2 + lv_label.get_width() + 6, 5))

        # Lives as pips
        pip_x = SCREEN_WIDTH - 14
        pip_r = 6
        for i in range(3):
            col = NEON_PINK if i < self.lives else (35, 40, 55)
            cx  = pip_x - i * (pip_r * 2 + 4)
            pygame.draw.circle(self.screen, col, (cx, bar_h // 2), pip_r)
            pygame.draw.circle(self.screen, NEON_PINK, (cx, bar_h // 2), pip_r, 1)

    # ── Draw ─────────────────────────────────────────────────────
    def draw(self):
        self._tick += 1
        self._draw_bg()

        if self.state == STATE_TITLE:
            # Glowing title
            pulse = int(20 + 12 * math.sin(self._tick * 0.05))
            glow = pygame.Surface((540, 90), pygame.SRCALPHA)
            glow.fill((*NEON_PINK, pulse))
            self.screen.blit(glow, (CENTER_X - 270, CENTER_Y - 120))

            self._draw_text("CYBER BREAKOUT", self.font_xl, NEON_PINK, CENTER_X, CENTER_Y - 75)
            self._draw_text("BRICK BY BRICK. SYSTEM BREACH INCOMING.", self.font_sm,
                            (80, 85, 110), CENTER_X, CENTER_Y - 25)

            pygame.draw.line(self.screen, NEON_PINK,
                             (120, CENTER_Y + 5), (SCREEN_WIDTH - 120, CENTER_Y + 5), 1)

            self._draw_text("←/→  or  A/D to move  |  ESC to menu", self.font_sm,
                            (100, 105, 135), CENTER_X, CENTER_Y + 50)

            alpha = int(180 + 75 * math.sin(self._tick * 0.08))
            prompt = self.font_md.render("PRESS SPACE TO START", True, NEON_YELLOW)
            prompt.set_alpha(alpha)
            self.screen.blit(prompt, prompt.get_rect(center=(CENTER_X, CENTER_Y + 115)))

        elif self.state == STATE_PLAYING:
            self.paddle.draw(self.screen)
            self.ball.draw(self.screen)
            for block in self.blocks:
                block.draw(self.screen)
            self._draw_hud()

        elif self.state == STATE_PAUSED:
            self.paddle.draw(self.screen)
            self.ball.draw(self.screen)
            for block in self.blocks:
                block.draw(self.screen)
            self._draw_hud()
            self._draw_overlay("PAUSED", NEON_YELLOW, "SPACE to resume  |  ESC to menu")

        elif self.state == STATE_GAME_OVER:
            self._draw_overlay("GAME OVER", (255, 55, 55), "SPACE to retry  |  ESC to menu")

        elif self.state == STATE_VICTORY:
            self._draw_overlay("SYSTEM HACKED!", NEON_GREEN, "SPACE to play again  |  ESC to menu")

        pygame.display.flip()

    # ── Main loop ─────────────────────────────────────────────────
    def run(self):
        pygame.display.set_caption("Cyber Breakout")
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        return self.return_to_menu
