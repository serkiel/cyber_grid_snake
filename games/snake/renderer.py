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
    NEON_GREEN,
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
        self._font_sm  = pygame.font.Font(None, 28)
        self._font_md  = pygame.font.Font(None, 40)
        self._font_lg  = pygame.font.Font(None, 60)
        self._font_xl  = pygame.font.Font(None, 80)
        self._font_hud = pygame.font.Font(None, 26)

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
        """Draw a styled top HUD banner with score and high-score."""
        bar_h = 30
        # Dark banner
        bar_surf = pygame.Surface((SCREEN_WIDTH, bar_h))
        bar_surf.set_alpha(180)
        bar_surf.fill((8, 10, 20))
        self.surface.blit(bar_surf, (0, 0))
        # Bottom border glow
        glow_line = pygame.Surface((SCREEN_WIDTH, 2))
        glow_line.set_alpha(60)
        glow_line.fill(NEON_CYAN)
        self.surface.blit(glow_line, (0, bar_h))
        pygame.draw.line(self.surface, NEON_CYAN, (0, bar_h), (SCREEN_WIDTH, bar_h), 1)

        # Score — left
        label_s = self._font_hud.render("SCORE", True, (70, 75, 100))
        val_s   = self._font_hud.render(str(score), True, NEON_CYAN)
        self.surface.blit(label_s, (14, 4))
        self.surface.blit(val_s,   (14 + label_s.get_width() + 6, 4))

        # High score — right
        label_h = self._font_hud.render("BEST", True, (70, 75, 100))
        val_h   = self._font_hud.render(str(high_score), True, NEON_YELLOW)
        total_w = label_h.get_width() + 6 + val_h.get_width()
        self.surface.blit(label_h, (SCREEN_WIDTH - total_w - 14, 4))
        self.surface.blit(val_h,   (SCREEN_WIDTH - val_h.get_width() - 14, 4))

        # Centre title tag
        tag = self._font_hud.render("CYBER-GRID SNAKE", True, (50, 55, 80))
        tag_rect = tag.get_rect(center=(SCREEN_WIDTH // 2, bar_h // 2))
        self.surface.blit(tag, tag_rect)

    def _draw_overlay_box(self, width: int, height: int,
                          border_color=None) -> pygame.Rect:
        """Draw a semi-transparent dark box centered on screen. Returns rect."""
        if border_color is None:
            border_color = NEON_CYAN
        box = pygame.Rect(0, 0, width, height)
        box.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # Full-screen dim
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 8, 140))
        self.surface.blit(dim, (0, 0))

        # Box background
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(215)
        overlay.fill((5, 8, 18))
        self.surface.blit(overlay, box.topleft)

        # Glow behind border
        glow_surf = pygame.Surface((width + 12, height + 12))
        glow_surf.set_alpha(30)
        glow_surf.fill(border_color)
        self.surface.blit(glow_surf, (box.x - 6, box.y - 6))

        pygame.draw.rect(self.surface, border_color, box, 2)
        return box

    def draw_title_screen(self, tick: int) -> None:
        """Draw the title/start screen with pulsing prompt."""
        self.clear()
        self.draw_grid()

        title_surf = self._font_xl.render(TITLE_TEXT, True, NEON_CYAN)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 55))

        # Glow behind title
        glow = pygame.Surface((title_rect.width + 50, title_rect.height + 24))
        glow.set_alpha(int(30 + 15 * math.sin(tick * 0.05)))
        glow.fill(NEON_CYAN)
        glow_rect = glow.get_rect(center=title_rect.center)
        self.surface.blit(glow, glow_rect)
        self.surface.blit(title_surf, title_rect)

        # Subtitle
        sub = self._font_sm.render("NAVIGATE THE GRID. EAT. GROW. DOMINATE.", True, (80, 85, 110))
        sub_rect = sub.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 15))
        self.surface.blit(sub, sub_rect)

        # Pulsing "Press ENTER" prompt
        alpha = int(120 + 135 * ((math.sin(tick * 0.08) + 1) / 2))
        prompt = self._font_md.render("PRESS ENTER TO START", True, NEON_YELLOW)
        prompt.set_alpha(alpha)
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.surface.blit(prompt, prompt_rect)

        # Controls hint
        hint = self._font_sm.render("Arrow Keys / WASD to move  |  P to pause  |  ESC to menu", True, (70, 75, 100))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 28))
        self.surface.blit(hint, hint_rect)

    def draw_pause_overlay(self) -> None:
        """Draw 'PAUSED' overlay with controls reminder."""
        box = self._draw_overlay_box(340, 110, NEON_YELLOW)

        text = self._font_lg.render("PAUSED", True, NEON_YELLOW)
        text_rect = text.get_rect(center=(box.centerx, box.y + 42))
        self.surface.blit(text, text_rect)

        hint = self._font_sm.render("P to resume  |  ESC to menu", True, (120, 125, 155))
        hint_rect = hint.get_rect(center=(box.centerx, box.y + 82))
        self.surface.blit(hint, hint_rect)

    def draw_game_over(self, score: int, high_score: int, tick: int = 0) -> None:
        """Draw styled game-over overlay with score info and pulsing restart prompt."""
        box = self._draw_overlay_box(400, 210, NEON_MAGENTA)

        go_surf = self._font_lg.render("GAME OVER", True, NEON_MAGENTA)
        go_rect = go_surf.get_rect(center=(box.centerx, box.y + 42))
        self.surface.blit(go_surf, go_rect)

        # Score row
        sc_surf = self._font_md.render(f"Score:  {score}", True, NEON_CYAN)
        sc_rect = sc_surf.get_rect(center=(box.centerx, box.y + 95))
        self.surface.blit(sc_surf, sc_rect)

        # High score row
        hi_surf = self._font_md.render(f"Best:    {high_score}", True, NEON_YELLOW)
        hi_rect = hi_surf.get_rect(center=(box.centerx, box.y + 135))
        self.surface.blit(hi_surf, hi_rect)

        # Pulsing restart prompt
        alpha = int(140 + 115 * ((math.sin(tick * 0.09) + 1) / 2))
        rs_surf = self._font_sm.render("SPACE to restart  |  ESC to menu", True, (160, 165, 190))
        rs_surf.set_alpha(alpha)
        rs_rect = rs_surf.get_rect(center=(box.centerx, box.y + 182))
        self.surface.blit(rs_surf, rs_rect)
