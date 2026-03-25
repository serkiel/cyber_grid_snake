import pygame
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BG_DARK, NEON_PINK, NEON_CYAN, NEON_GREEN, NEON_YELLOW

STATE_TITLE = "TITLE"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"
STATE_VICTORY = "VICTORY"

FPS = 60

class Paddle:
    def __init__(self):
        self.width = 100
        self.height = 15
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = SCREEN_HEIGHT - 40
        self.speed = 10
        self.color = NEON_PINK

    def move_left(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = 0

    def move_right(self):
        self.x += self.speed
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width

    def draw(self, surface):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.color, rect)
        # Glow
        glow = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*self.color, 60), glow.get_rect(), border_radius=5)
        surface.blit(glow, (self.x - 5, self.y - 5))

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.dx = 5
        self.dy = -5
        self.speed_multiplier = 1.0
        self.color = NEON_CYAN

    def update(self):
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
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        # Glow
        glow = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 60), (self.radius * 2, self.radius * 2), self.radius * 2)
        surface.blit(glow, (int(self.x) - self.radius * 2, int(self.y) - self.radius * 2))

class Block:
    def __init__(self, x, y, width, height, color, strength=1):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.strength = strength

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 1)

class BreakoutGame:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.return_to_menu = False
        self.state = STATE_TITLE
        
        self.font_lg = pygame.font.Font(None, 74)
        self.font_md = pygame.font.Font(None, 48)
        self.font_sm = pygame.font.Font(None, 36)
        
        self.reset_game()

    def reset_game(self):
        self.paddle = Paddle()
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
        self.blocks = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.create_blocks()

    def create_blocks(self):
        self.blocks.clear()
        rows = 4 + self.level
        cols = 10
        block_width = (SCREEN_WIDTH - 100) // cols
        block_height = 25
        
        colors = [NEON_PINK, NEON_CYAN, NEON_GREEN, NEON_YELLOW]
        
        for row in range(rows):
            for col in range(cols):
                x = 50 + col * block_width
                y = 80 + row * (block_height + 5)
                color = colors[row % len(colors)]
                self.blocks.append(Block(x, y, block_width - 2, block_height, color))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.return_to_menu = True
                    self.running = False
                
                if self.state == STATE_TITLE or self.state == STATE_GAME_OVER or self.state == STATE_VICTORY:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        if self.state != STATE_TITLE:
                            self.reset_game()
                        self.state = STATE_PLAYING

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
        paddle_rect = pygame.Rect(self.paddle.x, self.paddle.y, self.paddle.width, self.paddle.height)
        ball_rect = pygame.Rect(self.ball.x - self.ball.radius, self.ball.y - self.ball.radius, self.ball.radius * 2, self.ball.radius * 2)
        
        if ball_rect.colliderect(paddle_rect) and self.ball.dy > 0:
            self.ball.dy = -self.ball.dy
            # Change dx based on where it hit the paddle
            hit_pos = (self.ball.x - self.paddle.x) / self.paddle.width
            self.ball.dx = 10 * (hit_pos - 0.5)
            self.ball.speed_multiplier = min(1.5, self.ball.speed_multiplier + 0.02)

        # Block collision
        for block in self.blocks[:]:
            if ball_rect.colliderect(block.rect):
                self.blocks.remove(block)
                self.score += 10 * self.level
                self.ball.dy = -self.ball.dy
                break # Only break one block per frame

        # Bottom collision (lose life)
        if self.ball.y + self.ball.radius >= SCREEN_HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.state = STATE_GAME_OVER
            else:
                self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
                self.paddle = Paddle()

        # Level complete
        if len(self.blocks) == 0:
            self.level += 1
            if self.level > 5:
                self.state = STATE_VICTORY
            else:
                self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
                self.paddle = Paddle()
                self.create_blocks()

    def draw_text(self, text, font, color, y, center=True, x=0):
        surface = font.render(text, True, color)
        if center:
            rect = surface.get_rect(center=(SCREEN_WIDTH // 2, y))
        else:
            rect = surface.get_rect(topleft=(x, y))
        self.screen.blit(surface, rect)

    def draw(self):
        self.screen.fill(BG_DARK)
        
        if self.state == STATE_TITLE:
            self.draw_text("CYBER BREAKOUT", self.font_lg, NEON_PINK, SCREEN_HEIGHT // 3)
            self.draw_text("PRESS SPACE TO START", self.font_sm, NEON_CYAN, SCREEN_HEIGHT // 2)
            self.draw_text("Use Left/Right Arrows or A/D to move", self.font_sm, (150, 150, 150), SCREEN_HEIGHT // 2 + 50)
            
        elif self.state == STATE_PLAYING:
            self.paddle.draw(self.screen)
            self.ball.draw(self.screen)
            for block in self.blocks:
                block.draw(self.screen)
                
            # HUD
            self.draw_text(f"SCORE: {self.score}", self.font_sm, NEON_CYAN, 20, center=False, x=20)
            self.draw_text(f"LIVES: {self.lives}", self.font_sm, NEON_PINK, 20, center=False, x=SCREEN_WIDTH - 150)
            
        elif self.state == STATE_GAME_OVER:
            self.draw_text("GAME OVER", self.font_lg, (255, 50, 50), SCREEN_HEIGHT // 3)
            self.draw_text(f"FINAL SCORE: {self.score}", self.font_md, NEON_CYAN, SCREEN_HEIGHT // 2)
            self.draw_text("PRESS SPACE TO RESTART", self.font_sm, (150, 150, 150), SCREEN_HEIGHT // 2 + 60)
            
        elif self.state == STATE_VICTORY:
            self.draw_text("SYSTEM HACKED!", self.font_lg, NEON_GREEN, SCREEN_HEIGHT // 3)
            self.draw_text(f"FINAL SCORE: {self.score}", self.font_md, NEON_CYAN, SCREEN_HEIGHT // 2)
            self.draw_text("PRESS SPACE TO PLAY AGAIN", self.font_sm, (150, 150, 150), SCREEN_HEIGHT // 2 + 60)
            
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        return self.return_to_menu
