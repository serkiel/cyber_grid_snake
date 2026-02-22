"""
Cyber-Grid Snake — Configuration and constants.
Centralizes all tunable values for easy sharing with collaborators.
"""

# Grid
GRID_WIDTH = 20   # number of cells horizontally
GRID_HEIGHT = 16  # number of cells vertically
CELL_SIZE = 32    # pixels per cell

# Derived
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 12           # Default fallback
START_FPS = 10     # How slow the game starts
FPS_INCREMENT = 0.5 # How much faster it gets per food
MAX_FPS = 25       # speed limit

# Neon palette (RGB)
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_GREEN = (57, 255, 20)
NEON_ORANGE = (255, 128, 0)
NEON_PINK = (255, 105, 180)
NEON_YELLOW = (255, 255, 0)
BG_DARK = (10, 12, 18)
GRID_LINE = (30, 35, 50)
GRID_GLOW = (20, 80, 90)

# Game
INITIAL_SNAKE_LENGTH = 3
SNAKE_HEAD_COLOR = NEON_CYAN
SNAKE_BODY_COLOR = NEON_GREEN
FOOD_COLOR = NEON_MAGENTA
GRID_ALPHA = 80

# Title
TITLE_TEXT = "CYBER-GRID SNAKE"
