# Cyber-Grid Snake

Neon-style Snake game built with Python and Pygame. Clean OOP structure for easy collaboration.

## Setup

```bash
cd d:\Uni\Code\cyber_grid_snake
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Controls

- **Arrow keys / WASD** — Change direction
- **ENTER** — Start game from title screen
- **P** — Pause / resume
- **SPACE** — Restart after game over
- **ESC** — Quit

## Features

- Neon cyber-grid visual theme with glowing cells
- Pulsing food animation
- Progressive speed increase as you score
- Session high-score tracking
- Title screen and styled game-over overlay

## Project Structure

- `main.py` — Entry point; creates and runs `Game`
- `game.py` — `Game` class: state machine, loop, input, update, draw
- `snake.py` — `Snake` class: body, direction queue, move, grow
- `food.py` — `Food` class: spawn, respawn, pulse animation
- `grid_renderer.py` — `GridRenderer` class: neon grid, overlays, HUD
- `config.py` — Constants: grid size, colors, FPS, title text
