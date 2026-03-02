"""
Cyber-Grid Snake — Grid and neon rendering (OOP).
Draws the cyber-style grid, game elements with glow effects,
title screen, pause overlay, and game-over screen.
"""

import math
import pygame
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import (
    CELL_SIZE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    GRID_WIDTH,
    GRID_HEIGHT,
    BG_DARK,
    GRID_LINE,
    GRID_ALPHA,
    NEON_CYAN,
    NEON_MAGENTA,
    NEON_YELLOW,
)

TITLE_TEXT = "CYBER-GRID SNAKE"


class SnakeRenderer:
    """Handles all drawing: background, grid lines, snake, food, UI overlays."""

    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self._grid_surface = None
        self._build_grid_surface()

        # Pre-create fonts (avoids re-creating every frame)
        self._font_sm = pygame.font.Font(None, 30)
        self._font_md = pygame.font.Font(None, 40)
        self._font_lg = pygame.font.Font(None, 60)
        self._font_xl = pygame.font.Font(None, 80)

    def _build_grid_surface(self) -> None:
        """Pre-render grid lines onto a semi-transparent surface."""
        self._grid_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._grid_surface.set_alpha(GRID_ALPHA)
        self._grid_surface.fill(BG_DARK)
        for x in range(0, SCREEN_WIDTH + 1, CELL_SIZE):
            pygame.draw.line(
                self._grid_surface, GRID_LINE, (x, 0), (x, SCREEN_HEIGHT), 1
            )
        for y in range(0, SCREEN_HEIGHT + 1, CELL_SIZE):
            pygame.draw.line(
                self._grid_surface, GRID_LINE, (0, y), (SCREEN_WIDTH, y), 1
            )

    # ── Background ──────────────────────────────────────────────

    def clear(self) -> None:
        """Fill screen with background color."""
        self.surface.fill(BG_DARK)

    def draw_grid(self) -> None:
        """Blit the pre-rendered grid overlay."""
        if self._grid_surface:
            self.surface.blit(self._grid_surface, (0, 0))

    # ── Cell drawing ────────────────────────────────────────────

    def _cell_to_rect(self, col: int, row: int) -> pygame.Rect:
        """Convert grid (col, row) to pixel rect with 1px margin for neon look."""
        margin = 1
        return pygame.Rect(
            col * CELL_SIZE + margin,
            row * CELL_SIZE + margin,
            CELL_SIZE - 2 * margin,
            CELL_SIZE - 2 * margin,
        )

    def draw_cell_glow(self, col: int, row: int, color: tuple[int, int, int],
                       alpha: int = 60) -> None:
        """Draw a soft glow behind a cell (larger, lower alpha)."""
        r = self._cell_to_rect(col, row)
        r.inflate_ip(CELL_SIZE // 2, CELL_SIZE // 2)
        s = pygame.Surface((r.width, r.height))
        s.set_alpha(alpha)
        s.fill(color)
        self.surface.blit(s, r.topleft)

    def draw_cell(self, col: int, row: int, color: tuple[int, int, int]) -> None:
        """Draw a filled neon cell with glow."""
        self.draw_cell_glow(col, row, color)
        pygame.draw.rect(self.surface, color, self._cell_to_rect(col, row))
        border = self._cell_to_rect(col, row)
        pygame.draw.rect(self.surface, color, border, 1)

    # ── Game elements ───────────────────────────────────────────

    def draw_snake(self, segments_with_colors: list[tuple[tuple[int, int], tuple[int, int, int]]]) -> None:
        """Draw all snake segments with their colors."""
        for (col, row), color in segments_with_colors:
            self.draw_cell(col, row, color)

    def draw_food(self, col: int, row: int, color: tuple[int, int, int],
                  pulse: float = 0.5) -> None:
        """Draw food with a pulsing glow."""
        glow_alpha = int(30 + pulse * 90)
        self.draw_cell_glow(col, row, color, alpha=glow_alpha)
        pygame.draw.rect(self.surface, color, self._cell_to_rect(col, row))

    # ── HUD & overlays ─────────────────────────────────────────

    def draw_hud(self, score: int, high_score: int) -> None:
        """Draw live score and high-score in the top corners."""
        score_surf = self._font_sm.render(f"SCORE: {score}", True, NEON_CYAN)
        self.surface.blit(score_surf, (14, 10))

        hi_surf = self._font_sm.render(f"HI: {high_score}", True, NEON_YELLOW)
        hi_rect = hi_surf.get_rect(topright=(SCREEN_WIDTH - 14, 10))
        self.surface.blit(hi_surf, hi_rect)

    def _draw_overlay_box(self, width: int, height: int) -> pygame.Rect:
        """Draw a semi-transparent dark box centered on screen. Returns rect."""
        box = pygame.Rect(0, 0, width, height)
        box.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(200)
        overlay.fill((5, 5, 15))
        self.surface.blit(overlay, box.topleft)
        pygame.draw.rect(self.surface, NEON_CYAN, box, 2)
        return box

    def draw_title_screen(self, tick: int) -> None:
        """Draw the title/start screen with pulsing prompt."""
        self.clear()
        self.draw_grid()

        title_surf = self._font_xl.render(TITLE_TEXT, True, NEON_CYAN)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))

        glow = pygame.Surface((title_rect.width + 40, title_rect.height + 20))
        glow.set_alpha(40)
        glow.fill(NEON_CYAN)
        glow_rect = glow.get_rect(center=title_rect.center)
        self.surface.blit(glow, glow_rect)
        self.surface.blit(title_surf, title_rect)

        alpha = int(120 + 135 * ((math.sin(tick * 0.08) + 1) / 2))
        prompt = self._font_md.render("Press ENTER to start", True, NEON_YELLOW)
        prompt.set_alpha(alpha)
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.surface.blit(prompt, prompt_rect)

        hint = self._font_sm.render("Arrow Keys / WASD to move  |  P to pause  |  ESC to quit", True, (100, 100, 130))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        self.surface.blit(hint, hint_rect)

    def draw_pause_overlay(self) -> None:
        """Draw 'PAUSED' text with dark overlay."""
        box = self._draw_overlay_box(280, 80)
        text = self._font_lg.render("PAUSED", True, NEON_YELLOW)
        text_rect = text.get_rect(center=box.center)
        self.surface.blit(text, text_rect)

    def draw_game_over(self, score: int, high_score: int) -> None:
        """Draw styled game-over overlay with score info."""
        box = self._draw_overlay_box(380, 180)

        go_surf = self._font_lg.render("GAME OVER", True, NEON_MAGENTA)
        go_rect = go_surf.get_rect(center=(box.centerx, box.y + 40))
        self.surface.blit(go_surf, go_rect)

        sc_surf = self._font_md.render(f"Score: {score}", True, NEON_CYAN)
        sc_rect = sc_surf.get_rect(center=(box.centerx, box.y + 85))
        self.surface.blit(sc_surf, sc_rect)

        hi_surf = self._font_md.render(f"Best: {high_score}", True, NEON_YELLOW)
        hi_rect = hi_surf.get_rect(center=(box.centerx, box.y + 120))
        self.surface.blit(hi_surf, hi_rect)

        rs_surf = self._font_sm.render("SPACE to restart", True, (160, 160, 180))
        rs_rect = rs_surf.get_rect(center=(box.centerx, box.y + 155))
        self.surface.blit(rs_surf, rs_rect)
