import pygame
import random
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from games.reaction.entities import Player, Item, ITEM_FOOD, ITEM_OBSTACLE
from games.reaction.renderer import ReactionRenderer

STATE_TITLE = "TITLE"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"

FPS = 60

class ReactionGame:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.renderer = ReactionRenderer(self.screen)
        
        # Player sits static on the left side
        self.player = Player(150, SCREEN_HEIGHT // 2)
        
        self.state = STATE_TITLE
        self.running = True
        self.return_to_menu = False
        
        self.score = 0
        self.items = []
        self._tick = 0
        self.bg_offset = 0
        self.spawn_timer = 0
        self.base_speed = 8
        try:
            self.sfx_eat = pygame.mixer.Sound("eat.wav")
            self.sfx_nav = pygame.mixer.Sound("nav.wav")
            self.sfx_crash = pygame.mixer.Sound("crash.wav")
        except:
            self.sfx_eat = None
            self.sfx_nav = None
            self.sfx_crash = None
        
    def _start_game(self):
        self.player.reset()
        self.score = 0
        self.items = []
        self._tick = 0
        self.bg_offset = 0
        self.base_speed = 8
        self.spawn_timer = 60
        self.state = STATE_PLAYING
        
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type != pygame.KEYDOWN:
                continue
                
            key = event.key
            if key == pygame.K_ESCAPE:
                self.return_to_menu = True
                self.running = False
                return
                
            if self.state == STATE_TITLE:
                if key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._start_game()
            elif self.state == STATE_PLAYING:
                if key == pygame.K_z:
                    self.player.eat()
                elif key == pygame.K_c:
                    self.player.dodge()
            elif self.state == STATE_GAME_OVER:
                if key == pygame.K_SPACE:
                    self._start_game()

    def _update(self):
        if self.state != STATE_PLAYING:
            return
            
        self.bg_offset += (self.base_speed * 0.5)
            
        self.player.update()
        
        # Difficulty scales over time
        self.base_speed = 8 + (self.score * 0.2)
        if self.base_speed > 25:
            self.base_speed = 25
            
        # Spawn logic
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            spawn_x = SCREEN_WIDTH + 50
            spawn_y = SCREEN_HEIGHT // 2
            
            # 50/50 chance of food or obstacle
            item_type = ITEM_FOOD if random.random() < 0.5 else ITEM_OBSTACLE
            
            speed = self.base_speed + random.uniform(-1, 2)
            self.items.append(Item(spawn_x, spawn_y, item_type, speed))
            
            # Time until next spawn
            min_gap = 40
            max_gap = max(40, int(150 - (self.score * 1.5)))
            self.spawn_timer = random.randint(min_gap, max_gap)
            
        # Update items
        for item in self.items:
            item.update()
            
        # Collision
        self._check_collisions()
        
        # Cleanup off-screen items
        self.items = [i for i in self.items if i.active and i.x > -50]
        
        if self.player.lives <= 0 and self.player.state_timer <= 0:
            self.state = STATE_GAME_OVER

    def _check_collisions(self):
        hitbox = pygame.Rect(
            self.player.x - self.player.base_radius,
            self.player.y - self.player.base_radius,
            self.player.base_radius * 2,
            self.player.base_radius * 2
        )
        
        for item in self.items:
            if not item.active:
                continue
                
            # Larger effective item hitbox to ensure fast moving objects hit
            item_rect = pygame.Rect(
                item.x - item.radius - int(item.speed),
                item.y - item.radius,
                item.radius * 2 + int(item.speed),
                item.radius * 2
            )
            
            if hitbox.colliderect(item_rect):
                item.active = False
                
                if item.type == ITEM_FOOD:
                    if self.player.state == "EAT":
                        if getattr(self, 'sfx_eat', None): self.sfx_eat.play()
                        self.score += 10
                    else:
                        pass # Missed food
                elif item.type == ITEM_OBSTACLE:
                    if self.player.state == "DODGE":
                        if getattr(self, 'sfx_nav', None): self.sfx_nav.play()
                        self.score += 5
                    else:
                        if getattr(self, 'sfx_crash', None): self.sfx_crash.play()
                        self.player.hurt()

    def _draw(self):
        self._tick += 1
        if self.state == STATE_TITLE:
            self.renderer.draw_title_screen(self._tick)
        elif self.state == STATE_PLAYING:
            self.renderer.draw_bg(self.bg_offset)
            self.renderer.draw_items(self.items, self._tick)
            self.renderer.draw_player(self.player, self._tick)
            self.renderer.draw_hud(self.score, self.player.lives)
        elif self.state == STATE_GAME_OVER:
            self.renderer.draw_bg(self.bg_offset)
            self.renderer.draw_items(self.items, self._tick)
            self.renderer.draw_player(self.player, self._tick)
            self.renderer.draw_hud(self.score, self.player.lives)
            self.renderer.draw_game_over(self.score, self._tick)
            
        pygame.display.flip()

    def run(self):
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)
        return self.return_to_menu
