"""
Cyber Arcade — Home page launcher.
Displays a collection of games and lets the player select one to play.
"""

import math
import time
import pygame
import sys, os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

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

# Game registry — each game has a name, description, color, and factory
GAMES = [
    {
        "name": "CYBER-GRID SNAKE",
        "desc": "Classic snake on a neon grid",
        "color": NEON_GREEN,
        "key": "1",
    },
    {
        "name": "CYBER DASH",
        "desc": "Geometry Dash-like runner",
        "color": NEON_MAGENTA,
        "key": "2",
    },
    {
        "name": "CYBER REACTION",
        "desc": "Fast-paced reaction arcade",
        "color": NEON_YELLOW,
        "key": "3",
    },
    {
        "name": "DATA DROP",
        "desc": "Match-3 dropping blocks puzzle",
        "color": NEON_CYAN,
        "key": "4",
    },
    {
        "name": "CYBER BREAKOUT",
        "desc": "Arcade classic brick breaker",
        "color": NEON_PINK,
        "key": "5",
    },
    {
        "name": "CYBER PONG",
        "desc": "Neon Pong versus the machine",
        "color": NEON_ORANGE,
        "key": "6",
    },
]


class Launcher:
    """Home screen that shows all available games for the arcade collection."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cyber Arcade")
        self.clock = pygame.time.Clock()

        self._font_sm = pygame.font.Font(None, 24)
        self._font_md = pygame.font.Font(None, 32)
        self._font_lg = pygame.font.Font(None, 50)
        self._font_xl = pygame.font.Font(None, 72)
        self._font_title = pygame.font.Font(None, 90)

        self.selected = 0
        self.running = True
        self._tick = 0
        self._bg_offset = 0.0

    def _launch_game(self, index: int) -> None:
        """Launch the selected game."""
        if index == 0:
            from games.snake.game import SnakeGame
            game = SnakeGame(self.screen, self.clock)
            result = game.run()
        elif index == 1:
            from games.cyber_dash.game import DashGame
            game = DashGame(self.screen, self.clock)
            result = game.run()
        elif index == 2:
            from games.reaction.game import ReactionGame
            game = ReactionGame(self.screen, self.clock)
            result = game.run()
        elif index == 3:
            from games.data_drop.game import DropGame
            game = DropGame(self.screen, self.clock)
            result = game.run()
        elif index == 4:
            from games.cyber_breakout.game import BreakoutGame
            game = BreakoutGame(self.screen, self.clock)
            result = game.run()
        elif index == 5:
            from games.cyber_pong.game import PongGame
            game = PongGame(self.screen, self.clock)
            result = game.run()
        else:
            return

        # After game returns, reset display caption
        pygame.display.set_caption("Cyber Arcade")

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type != pygame.KEYDOWN:
                continue

            key = event.key

            if key == pygame.K_ESCAPE:
                self.running = False
                return

            # Number keys for quick select
            if key == pygame.K_1:
                self._launch_game(0)
                return
            if key == pygame.K_2:
                self._launch_game(1)
                return
            if key == pygame.K_3:
                self._launch_game(2)
                return
            if key == pygame.K_4:
                self._launch_game(3)
                return
            if key == pygame.K_5:
                self._launch_game(4)
                return
            if key == pygame.K_6:
                self._launch_game(5)
                return

            # Arrow navigation (up/down/left/right all navigate)
            if key in (pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % len(GAMES)
            elif key in (pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % len(GAMES)
            elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._launch_game(self.selected)

    def _draw(self) -> None:
        self._tick += 1

        # ── Background ──────────────────────────────────────
        self.screen.fill(BG_DARK)
        self._bg_offset = (self._bg_offset + 0.5) % 40

        # Scrolling grid
        for x in range(-40, SCREEN_WIDTH + 40, 40):
            sx = x - int(self._bg_offset)
            pygame.draw.line(
                self.screen, (18, 22, 32),
                (sx, 0), (sx, SCREEN_HEIGHT), 1
            )
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(
                self.screen, (18, 22, 32),
                (0, y), (SCREEN_WIDTH, y), 1
            )

        # ── Title ───────────────────────────────────────────
        # Glow behind title
        title_text = "CYBER ARCADE"
        title_surf = self._font_title.render(title_text, True, NEON_CYAN)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 55))

        glow = pygame.Surface((title_rect.width + 60, title_rect.height + 20))
        glow.set_alpha(25 + int(10 * math.sin(self._tick * 0.05)))
        glow.fill(NEON_CYAN)
        glow_rect = glow.get_rect(center=title_rect.center)
        self.screen.blit(glow, glow_rect)
        self.screen.blit(title_surf, title_rect)

        # Subtitle
        sub = self._font_md.render("SELECT A GAME", True, (100, 110, 140))
        sub_rect = sub.get_rect(center=(SCREEN_WIDTH // 2, 95))
        self.screen.blit(sub, sub_rect)

        # Decorative line
        line_y = 115
        pygame.draw.line(self.screen, NEON_CYAN, (80, line_y), (SCREEN_WIDTH - 80, line_y), 1)
        # Glow on line
        line_glow = pygame.Surface((SCREEN_WIDTH - 160, 4))
        line_glow.set_alpha(40)
        line_glow.fill(NEON_CYAN)
        self.screen.blit(line_glow, (80, line_y - 1))

        # ── Game Cards ──────────────────────────────────────
        card_w = 560
        card_h = 72
        spacing = 7
        total_cards_h = len(GAMES) * card_h + (len(GAMES) - 1) * spacing
        start_y = max(125, (SCREEN_HEIGHT - total_cards_h) // 2 + 20)

        for i, game in enumerate(GAMES):
            y = start_y + i * (card_h + spacing)
            x = (SCREEN_WIDTH - card_w) // 2
            is_selected = (i == self.selected)

            # Card background
            card_rect = pygame.Rect(x, y, card_w, card_h)
            card_surf = pygame.Surface((card_w, card_h))

            if is_selected:
                card_surf.fill((20, 25, 40))
                card_surf.set_alpha(240)
            else:
                card_surf.fill((12, 15, 25))
                card_surf.set_alpha(200)
            self.screen.blit(card_surf, card_rect.topleft)

            # Selection glow
            if is_selected:
                glow_surf = pygame.Surface((card_w + 16, card_h + 16))
                glow_alpha = int(25 + 15 * math.sin(self._tick * 0.08))
                glow_surf.set_alpha(glow_alpha)
                glow_surf.fill(game["color"])
                self.screen.blit(glow_surf, (x - 8, y - 8))

            # Border
            border_color = game["color"] if is_selected else (40, 45, 60)
            border_width = 2 if is_selected else 1
            pygame.draw.rect(self.screen, border_color, card_rect, border_width)

            # Color accent bar on left
            accent_rect = pygame.Rect(x, y, 5, card_h)
            pygame.draw.rect(self.screen, game["color"], accent_rect)

            # Key shortcut badge
            key_text = self._font_md.render(game["key"], True, game["color"])
            key_rect = key_text.get_rect(center=(x + 35, y + card_h // 2))
            # Badge background
            badge = pygame.Rect(0, 0, 36, 36)
            badge.center = key_rect.center
            pygame.draw.rect(self.screen, (25, 30, 45), badge)
            pygame.draw.rect(self.screen, game["color"], badge, 1)
            self.screen.blit(key_text, key_rect)

            # Game name
            name_color = game["color"] if is_selected else NEON_CYAN
            name_surf = self._font_lg.render(game["name"], True, name_color)
            name_rect = name_surf.get_rect(topleft=(x + 65, y + 8))
            self.screen.blit(name_surf, name_rect)

            # Description
            desc_surf = self._font_sm.render(game["desc"], True, (120, 125, 150))
            desc_rect = desc_surf.get_rect(topleft=(x + 65, y + 46))
            self.screen.blit(desc_surf, desc_rect)

            # Selection arrow
            if is_selected:
                arrow_x = x + card_w - 35
                arrow_y = y + card_h // 2
                pulse = math.sin(self._tick * 0.12) * 5
                points = [
                    (arrow_x + pulse, arrow_y),
                    (arrow_x - 10 + pulse, arrow_y - 8),
                    (arrow_x - 10 + pulse, arrow_y + 8),
                ]
                pygame.draw.polygon(self.screen, game["color"], points)

        # ── Footer ──────────────────────────────────────────
        footer_y = SCREEN_HEIGHT - 30

        # Decorative top line of footer
        foot_line_y = SCREEN_HEIGHT - 45
        pygame.draw.line(self.screen, NEON_CYAN,
                         (80, foot_line_y), (SCREEN_WIDTH - 80, foot_line_y), 1)
        foot_glow = pygame.Surface((SCREEN_WIDTH - 160, 3))
        foot_glow.set_alpha(30)
        foot_glow.fill(NEON_CYAN)
        self.screen.blit(foot_glow, (80, foot_line_y - 1))

        hint = self._font_sm.render(
            "↑↓ ←→  Navigate  |  ENTER to play  |  ESC to quit",
            True, (70, 75, 95)
        )
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, footer_y))
        self.screen.blit(hint, hint_rect)

        # Animated neon version badge
        badge_alpha = int(160 + 60 * math.sin(self._tick * 0.04))
        ver_surf = self._font_sm.render("v1.0", True, NEON_CYAN)
        ver_surf.set_alpha(badge_alpha)
        ver_rect = ver_surf.get_rect(bottomright=(SCREEN_WIDTH - 12, SCREEN_HEIGHT - 8))
        # Badge background pill
        pill = pygame.Surface((ver_surf.get_width() + 14, ver_surf.get_height() + 6))
        pill.set_alpha(60)
        pill.fill(NEON_CYAN)
        self.screen.blit(pill, (ver_rect.x - 7, ver_rect.y - 3))
        pygame.draw.rect(self.screen, NEON_CYAN,
                         (ver_rect.x - 7, ver_rect.y - 3,
                          ver_surf.get_width() + 14, ver_surf.get_height() + 6), 1)
        self.screen.blit(ver_surf, ver_rect)

        pygame.display.flip()

    def run(self) -> None:
        """Main launcher loop."""
        while self.running:
            self._handle_events()
            self._draw()
            self.clock.tick(60)
        pygame.quit()
