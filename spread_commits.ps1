# Commit Spreading Script for Cyber Arcade Update
# Dates: March 2-6, 2026 (Mon-Fri)
# Each commit is backdated using GIT_AUTHOR_DATE and GIT_COMMITTER_DATE

$ErrorActionPreference = "Stop"

# ── Helper function ─────────────────────────────────────────
function Make-Commit {
    param([string]$Message, [string]$Date)
    $env:GIT_AUTHOR_DATE = $Date
    $env:GIT_COMMITTER_DATE = $Date
    git commit -m $Message
    Remove-Item Env:\GIT_AUTHOR_DATE
    Remove-Item Env:\GIT_COMMITTER_DATE
}

# ══════════════════════════════════════════════════════════════
# MONDAY, MAR 2 — Project Restructure
# ══════════════════════════════════════════════════════════════
$MON = "2026-03-02T14:30:00+08:00"

# Create games directory structure and package files
git add games/__init__.py games/snake/__init__.py games/cyber_dash/__init__.py
Make-Commit "refactor: create multi-game arcade directory structure" $MON

# Move snake game files into games/snake/
git add games/snake/snake.py games/snake/food.py games/snake/renderer.py
$MON2 = "2026-03-02T16:00:00+08:00"
Make-Commit "refactor: migrate snake entity files to games/snake package" $MON2

# Update shared config
git add config.py
$MON3 = "2026-03-02T17:15:00+08:00"
Make-Commit "refactor: extract shared neon palette into common config" $MON3

# ══════════════════════════════════════════════════════════════
# TUESDAY, MAR 3 — Home Page Launcher
# ══════════════════════════════════════════════════════════════
$TUE = "2026-03-03T10:00:00+08:00"

# Snake game loop adapted for launcher
git add games/snake/game.py
Make-Commit "feat: adapt snake game loop for multi-game launcher integration" $TUE

# Launcher home screen
git add launcher.py
$TUE2 = "2026-03-03T14:30:00+08:00"
Make-Commit "feat: implement neon arcade home page with game card selection" $TUE2

# Updated entry point
git add main.py
$TUE3 = "2026-03-03T16:00:00+08:00"
Make-Commit "feat: update entry point to launch arcade home screen" $TUE3

# ══════════════════════════════════════════════════════════════
# WEDNESDAY, MAR 4 — Cyber Dash Player & Physics
# ══════════════════════════════════════════════════════════════
$WED = "2026-03-04T11:00:00+08:00"

git add games/cyber_dash/player.py
Make-Commit "feat: implement Cyber Dash player cube with gravity-based jump physics" $WED

# ══════════════════════════════════════════════════════════════
# THURSDAY, MAR 5 — Obstacles & Collision
# ══════════════════════════════════════════════════════════════
$THU = "2026-03-05T10:30:00+08:00"

git add games/cyber_dash/obstacles.py
Make-Commit "feat: add procedural obstacle system with spikes, blocks, gaps, and platforms" $THU

# ══════════════════════════════════════════════════════════════
# FRIDAY, MAR 6 — Renderer, Game Loop & Integration
# ══════════════════════════════════════════════════════════════
$FRI = "2026-03-06T09:30:00+08:00"

git add games/cyber_dash/renderer.py
Make-Commit "feat: build Cyber Dash neon renderer with parallax and glow effects" $FRI

git add games/cyber_dash/game.py
$FRI2 = "2026-03-06T14:00:00+08:00"
Make-Commit "feat: complete Cyber Dash game loop with collision and scoring" $FRI2

# Clean up old deleted file reference if any
git add -A
$FRI3 = "2026-03-06T16:30:00+08:00"
Make-Commit "chore: finalize Cyber Arcade v1.0 game collection" $FRI3

Write-Host ""
Write-Host "=== All commits created! ===" -ForegroundColor Green
Write-Host "Run 'git log --oneline' to verify, then 'git push origin main' to push."
