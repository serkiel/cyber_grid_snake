"""
Cyber Pong — A neon-themed single-player Pong game.
Player controls the left paddle; a reactive AI controls the right.
Ball speed increases on each hit for escalating challenge.
"""

import pygame
import math
import random
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BG_DARK, NEON_ORANGE, NEON_CYAN, NEON_MAGENTA, NEON_GREEN, NEON_YELLOW
from telemetry_db import TelemetryDB

FPS = 60

# Game states
STATE_TITLE    = "TITLE"
STATE_PLAYING  = "PLAYING"
STATE_PAUSED   = "PAUSED"
STATE_WIN      = "WIN"
STATE_LOSE     = "LOSE"

# Gameplay constants
PADDLE_W       = 12
PADDLE_H       = 80
PADDLE_SPEED   = 6
AI_BASE_SPEED  = 4
BALL_RADIUS    = 9
BALL_INIT_SPEED = 5.0
BALL_MAX_SPEED  = 14.0
SPEED_INCREMENT = 0.35
WIN_SCORE      = 7
CENTER_X       = SCREEN_WIDTH // 2
CENTER_Y       = SCREEN_HEIGHT // 2
PADDING        = 24          # Paddle distance from edge


class Particle:
    """Short-lived glow spark used for hit effects."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 4.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(10, 22)
        self.max_life = self.life
        self.radius = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.92
        self.vy *= 0.92
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        r, g, b = self.color
        glow = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (r, g, b, alpha), (self.radius * 2, self.radius * 2), self.radius * 2)
        surface.blit(glow, (int(self.x) - self.radius * 2, int(self.y) - self.radius * 2))
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), self.radius)


class PlayerPaddle:
    def __init__(self):
        self.w = PADDLE_W
        self.h = PADDLE_H
        self.x = PADDING
        self.y = CENTER_Y - self.h // 2
        self.color = NEON_ORANGE
        self.prev_y = self.y

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, keys):
        self.prev_y = self.y
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += PADDLE_SPEED
        self.y = max(0, min(SCREEN_HEIGHT - self.h, self.y))

    def draw(self, surface):
        # Glow
        glow = pygame.Surface((self.w + 16, self.h + 16), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*self.color, 50), glow.get_rect(), border_radius=6)
        surface.blit(glow, (self.x - 8, self.y - 8))
        # Body
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
        # Bright centre line
        pygame.draw.rect(surface, (255, 220, 150), pygame.Rect(self.x + self.w // 2 - 1, self.y + 4, 2, self.h - 8))


class AIPaddle:
    def __init__(self):
        self.w = PADDLE_W
        self.h = PADDLE_H
        self.x = SCREEN_WIDTH - PADDING - self.w
        self.y = CENTER_Y - self.h // 2
        self.color = NEON_MAGENTA
        self.speed = AI_BASE_SPEED
        # Small reaction lag so the AI isn't perfect
        self._target_y = float(self.y)
        self._lag = 0.18        # interpolation factor

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, ball_y, ball_moving_right):
        """Track ball only when ball is coming toward us; add slight lag."""
        if ball_moving_right:
            self._target_y = ball_y - self.h // 2
        # Lazy interpolation
        diff = self._target_y - self.y
        move = min(abs(diff), self.speed) * (1 if diff > 0 else -1)
        self.y += move
        self.y = max(0, min(SCREEN_HEIGHT - self.h, self.y))

    def draw(self, surface):
        glow = pygame.Surface((self.w + 16, self.h + 16), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*self.color, 50), glow.get_rect(), border_radius=6)
        surface.blit(glow, (self.x - 8, self.y - 8))
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
        pygame.draw.rect(surface, (255, 150, 230), pygame.Rect(self.x + self.w // 2 - 1, self.y + 4, 2, self.h - 8))


class Ball:
    def __init__(self):
        self.reset()

    def reset(self, direction=1):
        """Re-center ball; direction=1 → towards AI, -1 → towards player."""
        self.x = float(CENTER_X)
        self.y = float(CENTER_Y)
        self.speed = BALL_INIT_SPEED
        angle = random.uniform(-math.pi / 4, math.pi / 4)
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)
        self.radius = BALL_RADIUS
        self.color = NEON_CYAN
        self.trail: list[tuple[float, float]] = []

    def update(self, player, ai) -> str | None:
        """
        Move ball and handle collisions.
        Returns 'player_scored', 'ai_scored', or None.
        """
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy

        # Wall bounce (top/bottom)
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy = abs(self.vy)
        elif self.y + self.radius >= SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius
            self.vy = -abs(self.vy)

        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius,
                                self.radius * 2, self.radius * 2)

        # Player paddle collision
        if ball_rect.colliderect(player.rect) and self.vx < 0:
            self.vx = abs(self.vx)
            # Spin: add some of the paddle's velocity
            offset = (self.y - (player.y + player.h / 2)) / (player.h / 2)
            self.vy = offset * self.speed
            self._boost()
            self.x = player.x + player.w + self.radius + 1
            return "hit_player"

        # AI paddle collision
        if ball_rect.colliderect(ai.rect) and self.vx > 0:
            self.vx = -abs(self.vx)
            offset = (self.y - (ai.y + ai.h / 2)) / (ai.h / 2)
            self.vy = offset * self.speed
            self._boost()
            self.x = ai.x - self.radius - 1
            return "hit_ai"

        # Scoring
        if self.x + self.radius < 0:
            return "ai_scored"
        if self.x - self.radius > SCREEN_WIDTH:
            return "player_scored"

        return None

    def _boost(self):
        self.speed = min(BALL_MAX_SPEED, self.speed + SPEED_INCREMENT)
        # Normalize velocity to new speed
        mag = math.hypot(self.vx, self.vy)
        if mag > 0:
            self.vx = (self.vx / mag) * self.speed
            self.vy = (self.vy / mag) * self.speed

    def draw(self, surface):
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(160 * (i / len(self.trail)))
            r = max(1, int(self.radius * (i / len(self.trail))))
            tsurf = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            pygame.draw.circle(tsurf, (*self.color, alpha), (r * 2, r * 2), r * 2)
            surface.blit(tsurf, (int(tx) - r * 2, int(ty) - r * 2))
        # Glow
        glow = pygame.Surface((self.radius * 5, self.radius * 5), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 70),
                           (self.radius * 2, self.radius * 2), self.radius * 2)
        surface.blit(glow, (int(self.x) - self.radius * 2, int(self.y) - self.radius * 2))
        # Core
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius // 2)


class PongGame:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.return_to_menu = False
        self.state = STATE_TITLE

        self.font_xl  = pygame.font.Font(None, 90)
        self.font_lg  = pygame.font.Font(None, 64)
        self.font_md  = pygame.font.Font(None, 42)
        self.font_sm  = pygame.font.Font(None, 28)

        self._tick = 0
        self._particles: list[Particle] = []
        self._bg_offset = 0.0

        try:
            self.sfx_nav = pygame.mixer.Sound("nav.wav")
            self.sfx_crash = pygame.mixer.Sound("crash.wav")
        except:
            self.sfx_nav = None
            self.sfx_crash = None

        self.reset_game()

    # ────────────────────────────────── setup ──
    def reset_game(self):
        self.player = PlayerPaddle()
        self.ai     = AIPaddle()
        self.ball   = Ball()
        self.player_score = 0
        self.ai_score     = 0
        self._rally       = 0    # track consecutive hits for stat display
        self._flash_timer = 0    # white-flash on score
        self.session_start = time.time()

    # ────────────────────────────────── helpers ──
    def _spawn_particles(self, x, y, color, n=18):
        for _ in range(n):
            self._particles.append(Particle(x, y, color))

    def _draw_text(self, text, font, color, cx, cy):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(cx, cy))
        self.screen.blit(surf, rect)

    def _draw_dashed_center(self):
        dash_h = 14
        gap    = 8
        x = CENTER_X - 1
        y = 0
        while y < SCREEN_HEIGHT:
            pygame.draw.rect(self.screen, (40, 50, 70), (x, y, 2, dash_h))
            y += dash_h + gap

    def _draw_bg(self):
        self.screen.fill(BG_DARK)
        self._bg_offset = (self._bg_offset + 0.3) % 40
        for x in range(-40, SCREEN_WIDTH + 40, 40):
            sx = x - int(self._bg_offset)
            pygame.draw.line(self.screen, (14, 18, 28), (sx, 0), (sx, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (14, 18, 28), (0, y), (SCREEN_WIDTH, y), 1)

    # ────────────────────────────────── events ──
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                    elif self.state == STATE_PAUSED:
                        self.return_to_menu = True
                        self.running = False
                    else:
                        self.return_to_menu = True
                        self.running = False

                # P key toggles pause
                if event.key == pygame.K_p:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSED
                    elif self.state == STATE_PAUSED:
                        self.state = STATE_PLAYING

                if self.state == STATE_TITLE:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.state = STATE_PLAYING

                elif self.state == STATE_PAUSED:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.state = STATE_PLAYING

                elif self.state in (STATE_WIN, STATE_LOSE):
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.reset_game()
                        self.state = STATE_PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        self.return_to_menu = True
                        self.running = False

    # ────────────────────────────────── update ──
    def _update(self):
        if self.state != STATE_PLAYING:
            return

        self._tick += 1
        if self._flash_timer > 0:
            self._flash_timer -= 1

        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.ai.update(self.ball.y, self.ball.vx > 0)

        result = self.ball.update(self.player, self.ai)

        if result == "hit_player":
            if getattr(self, 'sfx_nav', None): self.sfx_nav.play()
            self._spawn_particles(self.player.x + self.player.w, self.ball.y, NEON_ORANGE)
            self._rally += 1
        elif result == "hit_ai":
            if getattr(self, 'sfx_nav', None): self.sfx_nav.play()
            self._spawn_particles(self.ai.x, self.ball.y, NEON_MAGENTA)
            self._rally += 1
        elif result == "player_scored":
            if getattr(self, 'sfx_crash', None): self.sfx_crash.play()
            self._spawn_particles(SCREEN_WIDTH - 20, self.ball.y, NEON_CYAN, 30)
            self.player_score += 1
            self._rally = 0
            self._flash_timer = 18
            if self.player_score >= WIN_SCORE:
                end_time = time.time()
                duration = int(end_time - getattr(self, 'session_start', end_time))
                TelemetryDB.log_game("Cyber Pong", getattr(self, 'session_start', end_time), end_time, duration, self.player_score)
                self.state = STATE_WIN
            else:
                self.ball.reset(direction=-1)     # serve toward AI
        elif result == "ai_scored":
            if getattr(self, 'sfx_crash', None): self.sfx_crash.play()
            self._spawn_particles(20, self.ball.y, NEON_MAGENTA, 30)
            self.ai_score += 1
            self._rally = 0
            self._flash_timer = 18
            if self.ai_score >= WIN_SCORE:
                end_time = time.time()
                duration = int(end_time - getattr(self, 'session_start', end_time))
                TelemetryDB.log_game("Cyber Pong", getattr(self, 'session_start', end_time), end_time, duration, self.player_score)
                self.state = STATE_LOSE
            else:
                self.ball.reset(direction=1)      # serve toward player

        # update particles
        for p in self._particles:
            p.update()
        self._particles = [p for p in self._particles if p.life > 0]

    # ────────────────────────────────── draw ──
    def _draw(self):
        self._draw_bg()

        if self.state == STATE_TITLE:
            self._draw_title()
        elif self.state == STATE_PLAYING:
            self._draw_game()
        elif self.state == STATE_PAUSED:
            self._draw_game()
            self._draw_overlay("PAUSED", NEON_ORANGE, "SPACE / P to resume  |  ESC to menu")
        elif self.state == STATE_WIN:
            self._draw_game()
            self._draw_overlay("YOU WIN!", NEON_GREEN, "SPACE to play again  |  ESC to menu")
        elif self.state == STATE_LOSE:
            self._draw_game()
            self._draw_overlay("GAME OVER", (255, 60, 60), "SPACE to retry  |  ESC to menu")

        pygame.display.flip()

    def _draw_title(self):
        # Glow behind title
        pulse = 20 + int(10 * math.sin(self._tick * 0.05))
        glow = pygame.Surface((520, 90), pygame.SRCALPHA)
        glow.fill((*NEON_ORANGE, pulse))
        self.screen.blit(glow, (CENTER_X - 260, CENTER_Y - 120))

        self._draw_text("CYBER PONG", self.font_xl, NEON_ORANGE, CENTER_X, CENTER_Y - 80)
        self._draw_text("VS THE MACHINE", self.font_md, NEON_CYAN, CENTER_X, CENTER_Y - 22)

        pygame.draw.line(self.screen, NEON_ORANGE, (120, CENTER_Y + 10), (SCREEN_WIDTH - 120, CENTER_Y + 10), 1)

        self._draw_text("First to 7 points wins", self.font_sm, (130, 135, 160), CENTER_X, CENTER_Y + 50)
        self._draw_text("W / S  or  ↑ / ↓  to move your paddle", self.font_sm, (100, 105, 135), CENTER_X, CENTER_Y + 85)

        # Pulsing prompt
        alpha = int(180 + 75 * math.sin(self._tick * 0.08))
        prompt = self.font_md.render("PRESS SPACE TO START", True, NEON_YELLOW)
        prompt.set_alpha(alpha)
        rect = prompt.get_rect(center=(CENTER_X, CENTER_Y + 145))
        self.screen.blit(prompt, rect)

        self._tick += 1

    def _draw_game(self):
        self._draw_dashed_center()

        # Score flash
        if self._flash_timer > 0:
            fl = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(30 * (self._flash_timer / 18))
            fl.fill((255, 255, 255, alpha))
            self.screen.blit(fl, (0, 0))

        # HUD — scores
        self._draw_text(str(self.player_score), self.font_lg, NEON_ORANGE,
                        CENTER_X - 100, 38)
        self._draw_text(str(self.ai_score),     self.font_lg, NEON_MAGENTA,
                        CENTER_X + 100, 38)

        # HUD — labels
        self._draw_text("YOU", self.font_sm, (100, 105, 135), CENTER_X - 100, 72)
        self._draw_text("CPU", self.font_sm, (100, 105, 135), CENTER_X + 100, 72)

        # Rally counter
        if self._rally >= 3:
            color = NEON_GREEN if self._rally < 8 else NEON_YELLOW
            self._draw_text(f"RALLY ×{self._rally}", self.font_sm, color, CENTER_X, 90)

        # Win-score indicator
        pip_y = 18
        for i in range(WIN_SCORE):
            cx = CENTER_X - 160 + i * 22
            col = NEON_ORANGE if i < self.player_score else (35, 40, 55)
            pygame.draw.circle(self.screen, col, (cx, pip_y), 7)
            pygame.draw.circle(self.screen, NEON_ORANGE, (cx, pip_y), 7, 1)

        for i in range(WIN_SCORE):
            cx = CENTER_X + 160 - i * 22
            col = NEON_MAGENTA if i < self.ai_score else (35, 40, 55)
            pygame.draw.circle(self.screen, col, (cx, pip_y), 7)
            pygame.draw.circle(self.screen, NEON_MAGENTA, (cx, pip_y), 7, 1)

        # Speed indicator
        speed_pct = (self.ball.speed - BALL_INIT_SPEED) / (BALL_MAX_SPEED - BALL_INIT_SPEED)
        bar_w = 80
        bar_h = 6
        bar_x = CENTER_X - bar_w // 2
        bar_y = SCREEN_HEIGHT - 22
        pygame.draw.rect(self.screen, (30, 35, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        fill_w = int(bar_w * speed_pct)
        if fill_w > 0:
            spd_color = NEON_GREEN if speed_pct < 0.5 else (NEON_YELLOW if speed_pct < 0.8 else (255, 60, 60))
            pygame.draw.rect(self.screen, spd_color, (bar_x, bar_y, fill_w, bar_h), border_radius=3)
        self._draw_text("SPEED", self.font_sm, (60, 65, 85), CENTER_X, SCREEN_HEIGHT - 35)

        # Game objects
        self.player.draw(self.screen)
        self.ai.draw(self.screen)
        self.ball.draw(self.screen)

        # Particles
        for p in self._particles:
            p.draw(self.screen)

    def _draw_overlay(self, title, color, hint):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Glow box
        box_w, box_h = 480, 180
        box_x = CENTER_X - box_w // 2
        box_y = CENTER_Y - box_h // 2
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((*color, 18))
        self.screen.blit(box_surf, (box_x, box_y))
        pygame.draw.rect(self.screen, color, (box_x, box_y, box_w, box_h), 2, border_radius=8)

        self._draw_text(title, self.font_lg, color, CENTER_X, CENTER_Y - 30)
        self._draw_text(hint,  self.font_sm, (140, 145, 170), CENTER_X, CENTER_Y + 35)

    # ────────────────────────────────── main loop ──
    def run(self):
        pygame.display.set_caption("Cyber Pong")
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)
        return self.return_to_menu
