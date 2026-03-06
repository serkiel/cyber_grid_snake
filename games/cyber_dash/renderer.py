"""
Cyber Dash — Neon renderer.
Draws player, obstacles, ground, scrolling background, HUD, and overlays.
"""

import math
import pygame
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BG_DARK,
    GRID_LINE,
    NEON_CYAN,
    NEON_MAGENTA,
    NEON_GREEN,
    NEON_YELLOW,
    NEON_ORANGE,
    NEON_PINK,
)

# Ground level — must match player.py
GROUND_Y = SCREEN_HEIGHT - 80


class DashRenderer:
    """All rendering for the Cyber Dash game."""

    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self._font_sm = pygame.font.Font(None, 28)
        self._font_md = pygame.font.Font(None, 40)
        self._font_lg = pygame.font.Font(None, 60)
        self._font_xl = pygame.font.Font(None, 80)
        self._font_title = pygame.font.Font(None, 90)
        self._bg_offset = 0.0

    # ── Background ──────────────────────────────────────────

    def draw_background(self, scroll_speed: float) -> None:
        """Draw scrolling grid background with parallax effect."""
        self.surface.fill(BG_DARK)

        self._bg_offset = (self._bg_offset + scroll_speed * 0.3) % 40

        # Vertical lines (scrolling)
        for x in range(-40, SCREEN_WIDTH + 40, 40):
            sx = x - int(self._bg_offset)
            pygame.draw.line(
                self.surface, (20, 25, 35),
                (sx, 0), (sx, SCREEN_HEIGHT), 1
            )

        # Horizontal lines (static)
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(
                self.surface, (20, 25, 35),
                (0, y), (SCREEN_WIDTH, y), 1
            )

        # Fade-out gradient at top
        grad = pygame.Surface((SCREEN_WIDTH, 60))
        grad.fill(BG_DARK)
        grad.set_alpha(180)
        self.surface.blit(grad, (0, 0))

    # ── Ground ──────────────────────────────────────────────

    def draw_ground(self, gaps: list[dict], scroll_offset: float = 0) -> None:
        """Draw the neon ground line, with gaps cut out."""
        # Ground fill
        ground_rect = pygame.Rect(0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y)

        # Draw ground segments (skipping gaps)
        gap_ranges = [(g['x'], g['x'] + g['w']) for g in gaps]
        segments = self._get_ground_segments(0, SCREEN_WIDTH, gap_ranges)

        for sx, ex in segments:
            rect = pygame.Rect(sx, GROUND_Y, ex - sx, SCREEN_HEIGHT - GROUND_Y)
            pygame.draw.rect(self.surface, (15, 20, 30), rect)
            # Neon top line
            pygame.draw.line(self.surface, NEON_CYAN, (sx, GROUND_Y), (ex, GROUND_Y), 2)
            # Glow
            glow_surf = pygame.Surface((ex - sx, 4))
            glow_surf.set_alpha(60)
            glow_surf.fill(NEON_CYAN)
            self.surface.blit(glow_surf, (sx, GROUND_Y - 2))

        # Draw "danger" indicators in gaps
        for g in gaps:
            # Red glow at bottom of gap
            if g['x'] + g['w'] > 0 and g['x'] < SCREEN_WIDTH:
                danger = pygame.Surface((min(g['w'], SCREEN_WIDTH), 20))
                danger.set_alpha(40)
                danger.fill(NEON_MAGENTA)
                self.surface.blit(danger, (max(0, g['x']), SCREEN_HEIGHT - 20))

    def _get_ground_segments(self, start: int, end: int, gaps: list) -> list:
        """Return list of (start_x, end_x) ground segments, cutting out gaps."""
        if not gaps:
            return [(start, end)]

        segments = []
        current = start
        for gx, gex in sorted(gaps):
            gx = max(gx, start)
            gex = min(gex, end)
            if gx > current:
                segments.append((current, gx))
            current = max(current, gex)
        if current < end:
            segments.append((current, end))
        return segments

    # ── Player ──────────────────────────────────────────────

    def draw_player(self, player, tick: int) -> None:
        """Draw the player cube with glow and rotation effect."""
        if not player.alive:
            return

        size = player.SIZE
        cx = player.x + size // 2
        cy = int(player.y) + size // 2

        # Glow behind player
        glow_size = size + 16
        glow_surf = pygame.Surface((glow_size, glow_size))
        glow_surf.set_alpha(35 + int(15 * math.sin(tick * 0.1)))
        glow_surf.fill(NEON_CYAN)
        self.surface.blit(glow_surf, (cx - glow_size // 2, cy - glow_size // 2))

        # Rotated cube
        cube_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(cube_surf, NEON_CYAN, (0, 0, size, size))
        pygame.draw.rect(cube_surf, (255, 255, 255), (0, 0, size, size), 2)
        # Inner highlight
        inner = 6
        pygame.draw.rect(cube_surf, (0, 200, 220), (inner, inner, size - 2 * inner, size - 2 * inner), 1)

        rotated = pygame.transform.rotate(cube_surf, -player.rotation)
        rot_rect = rotated.get_rect(center=(cx, cy))
        self.surface.blit(rotated, rot_rect)

        # Trail effect (a few fading cubes behind)
        if not player.on_ground:
            for i in range(1, 4):
                trail_surf = pygame.Surface((size - i * 6, size - i * 6), pygame.SRCALPHA)
                trail_alpha = max(10, 60 - i * 20)
                trail_surf.fill((*NEON_CYAN, trail_alpha))
                tr = trail_surf.get_rect(center=(cx - i * 8, cy + i * 4))
                self.surface.blit(trail_surf, tr)

    # ── Obstacles ───────────────────────────────────────────

    def draw_obstacles(self, obstacles: list[dict], tick: int) -> None:
        """Draw all obstacles with neon styling."""
        for obs in obstacles:
            if obs['x'] + obs['w'] < -10 or obs['x'] > SCREEN_WIDTH + 10:
                continue

            if obs['type'] == 'spike':
                self._draw_spike(obs, tick)
            elif obs['type'] == 'block':
                self._draw_block(obs, tick)
            elif obs['type'] == 'platform':
                self._draw_platform(obs, tick)
            # gaps are handled by draw_ground

    def _draw_spike(self, spike: dict, tick: int) -> None:
        """Draw a triangular spike with neon glow."""
        x, y, w, h = int(spike['x']), int(spike['y']), spike['w'], spike['h']

        # Triangle points
        points = [
            (x + w // 2, y),        # top
            (x, y + h),              # bottom-left
            (x + w, y + h),          # bottom-right
        ]

        # Glow
        glow_points = [
            (x + w // 2, y - 4),
            (x - 4, y + h + 4),
            (x + w + 4, y + h + 4),
        ]
        glow_surf = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
        offset_pts = [(p[0] - x + 10, p[1] - y + 10) for p in glow_points]
        pygame.draw.polygon(glow_surf, (*NEON_MAGENTA, 40), offset_pts)
        self.surface.blit(glow_surf, (x - 10, y - 10))

        # Spike body
        pygame.draw.polygon(self.surface, NEON_MAGENTA, points)
        pygame.draw.polygon(self.surface, (255, 100, 200), points, 2)

    def _draw_block(self, block: dict, tick: int) -> None:
        """Draw a rectangular block obstacle."""
        x, y, w, h = int(block['x']), int(block['y']), block['w'], block['h']
        rect = pygame.Rect(x, y, w, h)

        # Glow
        glow_surf = pygame.Surface((w + 12, h + 12))
        glow_surf.set_alpha(35)
        glow_surf.fill(NEON_ORANGE)
        self.surface.blit(glow_surf, (x - 6, y - 6))

        # Block body
        pygame.draw.rect(self.surface, NEON_ORANGE, rect)
        pygame.draw.rect(self.surface, (255, 180, 80), rect, 2)
        # Inner cross pattern
        pygame.draw.line(self.surface, (200, 100, 0), (x, y), (x + w, y + h), 1)
        pygame.draw.line(self.surface, (200, 100, 0), (x + w, y), (x, y + h), 1)

    def _draw_platform(self, plat: dict, tick: int) -> None:
        """Draw a floating platform."""
        x, y, w, h = int(plat['x']), int(plat['y']), plat['w'], plat['h']
        rect = pygame.Rect(x, y, w, h)

        # Glow
        glow_surf = pygame.Surface((w + 8, h + 16))
        glow_surf.set_alpha(30)
        glow_surf.fill(NEON_GREEN)
        self.surface.blit(glow_surf, (x - 4, y - 4))

        # Platform body
        pygame.draw.rect(self.surface, NEON_GREEN, rect)
        pygame.draw.rect(self.surface, (100, 255, 80), rect, 1)

    # ── HUD ─────────────────────────────────────────────────

    def draw_hud(self, score: int, high_score: int, attempt: int) -> None:
        """Draw score, high score, and attempt counter."""
        # Score
        score_text = self._font_md.render(f"{score}%", True, NEON_CYAN)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.surface.blit(score_text, score_rect)

        # High score
        hi_text = self._font_sm.render(f"BEST: {high_score}%", True, NEON_YELLOW)
        hi_rect = hi_text.get_rect(topright=(SCREEN_WIDTH - 14, 10))
        self.surface.blit(hi_text, hi_rect)

        # Attempt
        att_text = self._font_sm.render(f"ATT: {attempt}", True, (100, 100, 130))
        self.surface.blit(att_text, (14, 10))

    # ── Progress bar ────────────────────────────────────────

    def draw_progress_bar(self, progress: float) -> None:
        """Draw a thin progress bar at the top of the screen."""
        bar_h = 4
        filled_w = int(SCREEN_WIDTH * min(progress, 1.0))

        # Background
        pygame.draw.rect(self.surface, (30, 30, 50),
                         (0, SCREEN_HEIGHT - bar_h - 2, SCREEN_WIDTH, bar_h))

        # Filled portion with gradient feel
        if filled_w > 0:
            bar_surf = pygame.Surface((filled_w, bar_h))
            bar_surf.fill(NEON_GREEN)
            bar_surf.set_alpha(200)
            self.surface.blit(bar_surf, (0, SCREEN_HEIGHT - bar_h - 2))

    # ── Title Screen ────────────────────────────────────────

    def draw_title_screen(self, tick: int) -> None:
        """Draw the Cyber Dash title screen."""
        self.draw_background(3.0)

        # Draw some decorative ground
        self.draw_ground([], 0)

        # Title
        title_surf = self._font_title.render("CYBER DASH", True, NEON_MAGENTA)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))

        # Glow behind title
        glow = pygame.Surface((title_rect.width + 50, title_rect.height + 24))
        glow.set_alpha(35)
        glow.fill(NEON_MAGENTA)
        glow_rect = glow.get_rect(center=title_rect.center)
        self.surface.blit(glow, glow_rect)
        self.surface.blit(title_surf, title_rect)

        # Subtitle
        sub = self._font_md.render("A Geometry Dash-like runner", True, NEON_CYAN)
        sub_rect = sub.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))
        self.surface.blit(sub, sub_rect)

        # Pulsing prompt
        alpha = int(120 + 135 * ((math.sin(tick * 0.08) + 1) / 2))
        prompt = self._font_md.render("Press SPACE to play", True, NEON_YELLOW)
        prompt.set_alpha(alpha)
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.surface.blit(prompt, prompt_rect)

        # Controls hint
        hint = self._font_sm.render("SPACE / UP to jump  |  ESC to go back", True, (100, 100, 130))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        self.surface.blit(hint, hint_rect)

    # ── Game Over ───────────────────────────────────────────

    def draw_game_over(self, score: int, high_score: int, attempt: int) -> None:
        """Draw game over overlay."""
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((5, 5, 15))
        self.surface.blit(overlay, (0, 0))

        # Box
        box_w, box_h = 380, 220
        box = pygame.Rect(0, 0, box_w, box_h)
        box.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        box_surf = pygame.Surface((box_w, box_h))
        box_surf.set_alpha(220)
        box_surf.fill((8, 10, 20))
        self.surface.blit(box_surf, box.topleft)
        pygame.draw.rect(self.surface, NEON_MAGENTA, box, 2)

        # "CRASHED!" header
        go_surf = self._font_lg.render("CRASHED!", True, NEON_MAGENTA)
        go_rect = go_surf.get_rect(center=(box.centerx, box.y + 40))
        self.surface.blit(go_surf, go_rect)

        # Progress
        sc_surf = self._font_md.render(f"Progress: {score}%", True, NEON_CYAN)
        sc_rect = sc_surf.get_rect(center=(box.centerx, box.y + 90))
        self.surface.blit(sc_surf, sc_rect)

        # Best
        hi_surf = self._font_md.render(f"Best: {high_score}%", True, NEON_YELLOW)
        hi_rect = hi_surf.get_rect(center=(box.centerx, box.y + 130))
        self.surface.blit(hi_surf, hi_rect)

        # Attempt
        att_surf = self._font_sm.render(f"Attempt #{attempt}", True, (140, 140, 160))
        att_rect = att_surf.get_rect(center=(box.centerx, box.y + 165))
        self.surface.blit(att_surf, att_rect)

        # Restart prompt
        rs_surf = self._font_sm.render("SPACE to retry  |  ESC to menu", True, (160, 160, 180))
        rs_rect = rs_surf.get_rect(center=(box.centerx, box.y + 198))
        self.surface.blit(rs_surf, rs_rect)
