import pygame
import math
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BG_DARK, NEON_CYAN, NEON_GREEN, NEON_MAGENTA, NEON_YELLOW
)
from games.reaction.entities import ITEM_FOOD, ITEM_OBSTACLE

class ReactionRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 80)
        self.font_lg = pygame.font.Font(None, 50)
        self.font_md = pygame.font.Font(None, 36)
        self.font_sm = pygame.font.Font(None, 24)
        
    def draw_bg(self, bg_offset):
        self.screen.fill(BG_DARK)
        # Draw horizontal lines
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (18, 22, 32), (0, y), (SCREEN_WIDTH, y), 1)
        # Draw scrolling vertical lines
        for x in range(-40, SCREEN_WIDTH + 40, 40):
            sx = x - int(bg_offset) % 40
            pygame.draw.line(self.screen, (18, 22, 32), (sx, 0), (sx, SCREEN_HEIGHT), 1)

    def draw_glow(self, surface, color, rect, alpha):
        glow = pygame.Surface((rect.width + 20, rect.height + 20))
        glow.set_alpha(alpha)
        glow.fill(color)
        r = glow.get_rect(center=rect.center)
        surface.blit(glow, r)

    def draw_player(self, player, tick):
        color = NEON_CYAN
        radius = player.base_radius
        y_offset = 0
        
        if player.state == "EAT":
            color = NEON_GREEN
            radius += 10 # Expand
        elif player.state == "DODGE":
            color = NEON_CYAN
            y_offset = -40 # Jump up to dodge
        elif player.state == "HURT":
            color = (255, 0, 0) # Flash red
            if (tick // 4) % 2 == 0:
                color = BG_DARK # Flicker effect
                
        px, py = int(player.x), int(player.y + y_offset)
        
        # Outer glow
        pygame.draw.circle(self.screen, color, (px, py), radius + 4, 2)
        
        # Solid core with alpha
        core = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(core, (*color, 180), (radius, radius), radius)
        self.screen.blit(core, (px - radius, py - radius))
        
        # Eyes / Visor (depends on state)
        if player.state == "EAT":
            # wide open mouth
            pygame.draw.circle(self.screen, BG_DARK, (px + 10, py), 8)
        else:
            # visor
            pygame.draw.line(self.screen, BG_DARK, (px + 5, py - 5), (px + 15, py - 5), 4)

    def draw_items(self, items, tick):
        for item in items:
            if not item.active:
                continue
            x, y = int(item.x), int(item.y)
            if item.type == ITEM_FOOD:
                color = NEON_GREEN
                # Pulsing square
                pulse = 3 * math.sin(tick * 0.2)
                size = item.radius + pulse
                rect = pygame.Rect(0, 0, size * 2, size * 2)
                rect.center = (x, y)
                pygame.draw.rect(self.screen, color, rect, 2)
                pygame.draw.rect(self.screen, color, rect.inflate(-8, -8))
            elif item.type == ITEM_OBSTACLE:
                color = NEON_MAGENTA
                # Spiky triangle
                pulse = 3 * math.cos(tick * 0.3)
                r = item.radius + pulse
                points = [
                    (x - r, y + r),
                    (x + r, y + r),
                    (x, y - r)
                ]
                pygame.draw.polygon(self.screen, color, points, 2)
                # Inner line
                pygame.draw.line(self.screen, color, (x, y - r + 5), (x, y + r - 5), 2)

    def draw_hud(self, score, lives):
        # Score
        score_surf = self.font_lg.render(f"SCORE: {score}", True, NEON_YELLOW)
        self.screen.blit(score_surf, (20, 20))
        
        # Lives
        lives_text = f"LIVES: {'❤' * lives}"
        lives_surf = self.font_md.render(lives_text, True, NEON_MAGENTA)
        self.screen.blit(lives_surf, (20, 70))
        
        # Controls reminder
        controls = self.font_sm.render("[Z] EAT Food (Green)   [C] DODGE Obstacles (Pink)", True, NEON_CYAN)
        self.screen.blit(controls, (20, SCREEN_HEIGHT - 35))

    def draw_title_screen(self, tick):
        self.screen.fill(BG_DARK)
        
        title_surf = self.font_title.render("CYBER REACTION", True, NEON_YELLOW)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.draw_glow(self.screen, NEON_YELLOW, title_rect, int(30 + 15 * math.sin(tick * 0.1)))
        self.screen.blit(title_surf, title_rect)
        
        prompt_surf = self.font_md.render("PRESS SPACE TO START", True, NEON_CYAN)
        prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        
        # Blink prompt
        if (tick // 30) % 2 == 0:
            self.screen.blit(prompt_surf, prompt_rect)
            
        inst = self.font_sm.render("Z TO EAT  |  C TO DODGE  |  ESC TO MENU", True, (150, 160, 180))
        inst_rect = inst.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(inst, inst_rect)

    def draw_game_over(self, score, tick):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((10, 5, 10))
        self.screen.blit(overlay, (0, 0))
        
        over_surf = self.font_title.render("SYSTEM FAILURE", True, (255, 50, 50))
        over_rect = over_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(over_surf, over_rect)
        
        score_surf = self.font_lg.render(f"FINAL SCORE: {score}", True, NEON_YELLOW)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_surf, score_rect)
        
        prompt_surf = self.font_md.render("PRESS SPACE TO RETRY", True, NEON_CYAN)
        prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        if (tick // 30) % 2 == 0:
            self.screen.blit(prompt_surf, prompt_rect)
