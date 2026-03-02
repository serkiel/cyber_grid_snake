"""
Cyber Arcade — Shared configuration and constants.
Centralizes all tunable values shared across games.
"""

# Grid (used by Snake game)
GRID_WIDTH = 20   # number of cells horizontally
GRID_HEIGHT = 16  # number of cells vertically
CELL_SIZE = 32    # pixels per cell

# Screen
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE   # 640
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE  # 512

# Neon palette (RGB) — shared across all games
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_GREEN = (57, 255, 20)
NEON_ORANGE = (255, 128, 0)
NEON_PINK = (255, 105, 180)
NEON_YELLOW = (255, 255, 0)
BG_DARK = (10, 12, 18)
GRID_LINE = (30, 35, 50)
GRID_GLOW = (20, 80, 90)
GRID_ALPHA = 80
