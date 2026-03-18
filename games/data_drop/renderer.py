import pygame
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT, NEON_CYAN, NEON_MAGENTA, NEON_GREEN, NEON_YELLOW, NEON_ORANGE, BG_DARK

class DropRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 80)
        self.font_md = pygame.font.Font(None, 36)
        self.font_sm = pygame.font.Font(None, 24)
        
        # Grid layout
        self.cell_size = 40
        self.cols = 8
        self.rows = 12
        self.board_w = self.cols * self.cell_size
        self.board_h = self.rows * self.cell_size
        self.offset_x = (SCREEN_WIDTH - self.board_w) // 2
        self.offset_y = (SCREEN_HEIGHT - self.board_h) // 2
        
    def _draw_block(self, r, c, color, alpha=255, scale=1.0):
        if r < 0: return # Don't draw blocks off-screen
        
        size = int(self.cell_size * scale)
        padding = (self.cell_size - size) // 2
        
        x = self.offset_x + c * self.cell_size + padding
        y = self.offset_y + r * self.cell_size + padding
        
        rect = pygame.Rect(x, y, size, size)
        
        # Draw block
        surf = pygame.Surface((size, size))
        surf.fill((20, 20, 30))
        surf.set_alpha(alpha)
        self.screen.blit(surf, rect)
        
        # Glow border
        border_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(border_surf, (*color, alpha), border_surf.get_rect(), 2)
        
        # Inner fill
        inner_rect = pygame.Rect(4, 4, size - 8, size - 8)
        pygame.draw.rect(border_surf, (*color, max(0, alpha - 100)), inner_rect)
        
        self.screen.blit(border_surf, rect.topleft)

    def draw_title_screen(self, tick):
        self.screen.fill(BG_DARK)
        
        # Grid bg
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, (15, 20, 25), (i, 0), (i, SCREEN_HEIGHT))
        for i in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.line(self.screen, (15, 20, 25), (0, i), (SCREEN_WIDTH, i))
            
        title = self.font_title.render("DATA DROP", True, NEON_CYAN)
        trect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        
        # Add glow
        glow = pygame.Surface(title.get_size())
        glow.fill(NEON_CYAN)
        glow.set_alpha(int(20 + 20 * math.sin(tick * 0.1)))
        self.screen.blit(glow, (trect.x, trect.y))
        
        self.screen.blit(title, trect)
        
        # Subtitle
        pulse = abs(math.sin(tick * 0.05)) * 255
        sub = self.font_md.render("Press SPACE to Start", True, (int(pulse), int(pulse), int(pulse)))
        srect = sub.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(sub, srect)
        
        # Controls
        ctrl = self.font_sm.render("L/R: Move | UP: Cycle Colors | DOWN: Faster Drop", True, (100, 110, 140))
        crect = ctrl.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
        self.screen.blit(ctrl, crect)

    def draw_game(self, grid, piece, matching_cells, score, tick):
        self.screen.fill(BG_DARK)
        
        # Draw board border and background
        board_rect = pygame.Rect(self.offset_x, self.offset_y, self.board_w, self.board_h)
        pygame.draw.rect(self.screen, (12, 15, 22), board_rect)
        pygame.draw.rect(self.screen, NEON_CYAN, board_rect, 2)
        
        # Grid lines
        for r in range(self.rows):
            py = self.offset_y + r * self.cell_size
            pygame.draw.line(self.screen, (25, 30, 40), (self.offset_x, py), (self.offset_x + self.board_w, py))
        for c in range(self.cols):
            px = self.offset_x + c * self.cell_size
            pygame.draw.line(self.screen, (25, 30, 40), (px, self.offset_y), (px, self.offset_y + self.board_h))
            
        # Draw locked grid
        for r in range(self.rows):
            for c in range(self.cols):
                if grid[r][c]:
                    # If matching, flash it
                    if (r, c) in matching_cells:
                        if tick % 8 < 4:
                            self._draw_block(r, c, (255, 255, 255), scale=1.1)
                        else:
                            self._draw_block(r, c, grid[r][c], scale=1.1)
                    else:
                        self._draw_block(r, c, grid[r][c])
                        
        # Draw active piece
        if piece is not None:
            pr = piece['r']
            pc = piece['c']
            colors = piece['colors']
            # top is r-2, mid is r-1, bottom is r
            self._draw_block(pr - 2, pc, colors[0])
            self._draw_block(pr - 1, pc, colors[1])
            self._draw_block(pr, pc, colors[2])
            
            # Predict drop ghost
            ghost_r = pr
            while True:
                if ghost_r + 1 >= self.rows or grid[ghost_r + 1][pc] is not None:
                    break
                ghost_r += 1
                
            self._draw_block(ghost_r - 2, pc, colors[0], alpha=60)
            self._draw_block(ghost_r - 1, pc, colors[1], alpha=60)
            self._draw_block(ghost_r, pc, colors[2], alpha=60)
            
        # Draw HUD
        score_surf = self.font_md.render(f"SCORE: {score}", True, NEON_GREEN)
        self.screen.blit(score_surf, (20, 20))

    def draw_game_over(self, score, tick):
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        tit = self.font_title.render("SYSTEM FAILURE", True, (255, 50, 50))
        trect = tit.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        self.screen.blit(tit, trect)
        
        sc = self.font_md.render(f"FINAL THREAT ELIMINATED: {score}", True, NEON_GREEN)
        screct = sc.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        self.screen.blit(sc, screct)
        
        pulse = abs(math.sin(tick * 0.05)) * 255
        sub = self.font_sm.render("Press SPACE to Restart | ESC to Menu", True, (int(pulse), int(pulse), int(pulse)))
        srect = sub.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70))
        self.screen.blit(sub, srect)
