import pygame
import random
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from config import SCREEN_WIDTH, SCREEN_HEIGHT, NEON_CYAN, NEON_MAGENTA, NEON_GREEN, NEON_ORANGE, NEON_YELLOW
from games.data_drop.renderer import DropRenderer
from telemetry_db import TelemetryDB
import time

STATE_TITLE = "TITLE"
STATE_PLAYING = "PLAYING"
STATE_MATCHING = "MATCHING"
STATE_GAME_OVER = "GAME_OVER"

FPS = 60
COLORS = [NEON_CYAN, NEON_MAGENTA, NEON_GREEN, NEON_YELLOW, NEON_ORANGE]
COLS = 8
ROWS = 12

class DropGame:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.renderer = DropRenderer(self.screen)
        
        self.state = STATE_TITLE
        self.running = True
        self.return_to_menu = False
        
        self.score = 0
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        
        # A piece is a column of 3 blocks to make it like "Columns" (more fun / playable)
        self.current_piece = None 
        self._tick = 0
        self.base_fall_speed = 40
        self.fall_speed = 40
        self.fall_timer = 0
        
        self.matching_cells = set()
        self.match_timer = 0
        try:
            self.sfx_eat = pygame.mixer.Sound("eat.wav")
            self.sfx_nav = pygame.mixer.Sound("nav.wav")
            self.sfx_crash = pygame.mixer.Sound("crash.wav")
        except:
            self.sfx_eat = None
            self.sfx_nav = None
            self.sfx_crash = None
        
    def _start_game(self):
        self.score = 0
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.current_piece = None
        self._tick = 0
        self.base_fall_speed = 40
        self.fall_speed = self.base_fall_speed
        self.fall_timer = 0
        self.session_start = time.time()
        self.state = STATE_PLAYING
        self._spawn_piece()

    def _spawn_piece(self):
        c = COLS // 2
        # If top center is blocked, game over
        if self.grid[0][c] is not None or self.grid[1][c] is not None or self.grid[2][c] is not None:
            if getattr(self, 'sfx_crash', None): self.sfx_crash.play()
            
            end_time = time.time()
            duration = int(end_time - getattr(self, 'session_start', end_time))
            TelemetryDB.log_game("Data Drop", getattr(self, 'session_start', end_time), end_time, duration, self.score)
            
            self.state = STATE_GAME_OVER
            return
            
        self.current_piece = {
            'c': c,
            'r': 0, # Bottom block is at r (wait, blocks are top to bottom? Let's say r is block 2)
            # We'll use a vertical column of 3 blocks
            'colors': [random.choice(COLORS), random.choice(COLORS), random.choice(COLORS)] 
        }
        # Actually r is the highest cell (top), r+1 is middle, r+2 is bottom.
        # So r=0 means blocks at 0, 1, 2. But we want piece to spawn above screen ideally, or start at top.
        # Let's say top block is at r-2, mid at r-1, down is r.
        self.current_piece['r'] = 2
        
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
                if key == pygame.K_LEFT:
                    if getattr(self, 'sfx_nav', None): self.sfx_nav.play()
                    self._move_piece(-1)
                elif key == pygame.K_RIGHT:
                    if getattr(self, 'sfx_nav', None): self.sfx_nav.play()
                    self._move_piece(1)
                elif key == pygame.K_UP:
                    if getattr(self, 'sfx_nav', None): self.sfx_nav.play()
                    self._cycle_colors()
                elif key == pygame.K_DOWN:
                    self.fall_speed = 5 # Fast drop
                elif key == pygame.K_SPACE:
                    if getattr(self, 'sfx_nav', None): self.sfx_nav.play()
                    self._hard_drop()
            elif self.state == STATE_GAME_OVER:
                if key == pygame.K_SPACE:
                    self._start_game()

        # Reset drop speed on key up
        if self.state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            if not keys[pygame.K_DOWN]:
                self.fall_speed = self.base_fall_speed

    def _move_piece(self, dc):
        if not self.current_piece: return
        nc = self.current_piece['c'] + dc
        if nc < 0 or nc >= COLS: return
        
        # Check collision with grid blocks
        # current_piece spans r-2, r-1, r
        r = self.current_piece['r']
        for i in range(3):
            test_r = r - i
            if test_r >= 0 and self.grid[test_r][nc] is not None:
                return
        self.current_piece['c'] = nc

    def _cycle_colors(self):
        if not self.current_piece: return
        colors = self.current_piece['colors']
        # Shift colors: top moves to bottom, etc.
        self.current_piece['colors'] = [colors[2], colors[0], colors[1]]

    def _hard_drop(self):
        if not self.current_piece: return
        while self._move_down():
            pass

    def _move_down(self):
        if not self.current_piece: return False
        r = self.current_piece['r']
        c = self.current_piece['c']
        
        # Can it move down?
        if r + 1 >= ROWS or self.grid[r + 1][c] is not None:
            self._lock_piece()
            return False
            
        self.current_piece['r'] = r + 1
        return True

    def _lock_piece(self):
        r = self.current_piece['r']
        c = self.current_piece['c']
        colors = self.current_piece['colors']
        
        # Lock into grid
        # colors[0] is top (r-2), colors[1] is mid (r-1), colors[2] is bottom (r)
        if r - 2 >= 0: self.grid[r - 2][c] = colors[0]
        if r - 1 >= 0: self.grid[r - 1][c] = colors[1]
        self.grid[r][c] = colors[2]
        
        self.current_piece = None
        self._check_matches()

    def _check_matches(self):
        matched = set()
        
        # Horizontal
        for r in range(ROWS):
            for c in range(COLS - 2):
                if self.grid[r][c] is None: continue
                color = self.grid[r][c]
                if self.grid[r][c+1] == color and self.grid[r][c+2] == color:
                    matched.add((r, c))
                    matched.add((r, c+1))
                    matched.add((r, c+2))
                    # check beyond 3
                    k = c + 3
                    while k < COLS and self.grid[r][k] == color:
                        matched.add((r, k))
                        k += 1

        # Vertical
        for c in range(COLS):
            for r in range(ROWS - 2):
                if self.grid[r][c] is None: continue
                color = self.grid[r][c]
                if self.grid[r+1][c] == color and self.grid[r+2][c] == color:
                    matched.add((r, c))
                    matched.add((r+1, c))
                    matched.add((r+2, c))
                    k = r + 3
                    while k < ROWS and self.grid[k][c] == color:
                        matched.add((k, c))
                        k += 1

        # Diagonal Top-Left to Bottom-Right
        for r in range(ROWS - 2):
            for c in range(COLS - 2):
                if self.grid[r][c] is None: continue
                color = self.grid[r][c]
                if self.grid[r+1][c+1] == color and self.grid[r+2][c+2] == color:
                    matched.add((r, c))
                    matched.add((r+1, c+1))
                    matched.add((r+2, c+2))
                    kr, kc = r + 3, c + 3
                    while kr < ROWS and kc < COLS and self.grid[kr][kc] == color:
                        matched.add((kr, kc))
                        kr += 1; kc += 1

        # Diagonal Bottom-Left to Top-Right
        for r in range(2, ROWS):
            for c in range(COLS - 2):
                if self.grid[r][c] is None: continue
                color = self.grid[r][c]
                if self.grid[r-1][c+1] == color and self.grid[r-2][c+2] == color:
                    matched.add((r, c))
                    matched.add((r-1, c+1))
                    matched.add((r-2, c+2))
                    kr, kc = r - 3, c + 3
                    while kr >= 0 and kc < COLS and self.grid[kr][kc] == color:
                        matched.add((kr, kc))
                        kr -= 1; kc += 1

        if len(matched) > 0:
            if getattr(self, 'sfx_eat', None): self.sfx_eat.play()
            self.matching_cells = matched
            self.match_timer = 20 # frames to show match animation
            self.state = STATE_MATCHING
            self.score += len(matched) * 10 * (len(matched) - 2)
            
            # speed up slightly
            self.base_fall_speed = max(10, self.base_fall_speed - 0.5)
        else:
            self.state = STATE_PLAYING
            self._spawn_piece()

    def _resolve_matches(self):
        # Remove matched blocks
        for r, c in self.matching_cells:
            self.grid[r][c] = None
        self.matching_cells.clear()
        
        # Apply gravity
        for c in range(COLS):
            write_r = ROWS - 1
            for read_r in range(ROWS - 1, -1, -1):
                if self.grid[read_r][c] is not None:
                    # Move block down
                    val = self.grid[read_r][c]
                    self.grid[read_r][c] = None
                    self.grid[write_r][c] = val
                    write_r -= 1

        # Check for chain reactions
        self._check_matches()

    def _update(self):
        if self.state == STATE_PLAYING:
            if self.current_piece:
                self.fall_timer += 1
                if self.fall_timer >= self.fall_speed:
                    self.fall_timer = 0
                    self._move_down()
        elif self.state == STATE_MATCHING:
            self.match_timer -= 1
            if self.match_timer <= 0:
                self._resolve_matches()

    def _draw(self):
        self._tick += 1
        if self.state == STATE_TITLE:
            self.renderer.draw_title_screen(self._tick)
        elif self.state in (STATE_PLAYING, STATE_MATCHING, STATE_GAME_OVER):
            self.renderer.draw_game(self.grid, self.current_piece, self.matching_cells, self.score, self._tick)
            if self.state == STATE_GAME_OVER:
                self.renderer.draw_game_over(self.score, self._tick)
                
        pygame.display.flip()

    def run(self):
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)
        return self.return_to_menu
