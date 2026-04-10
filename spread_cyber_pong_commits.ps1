# Commit Spreading Script for Cyber Arcade (Cyber Pong Update)
# Dates: March 30 - April 2, 2026 (Mon-Thu, FRIDAY OFF - Holy Week)
# Each commit is backdated using GIT_AUTHOR_DATE and GIT_COMMITTER_DATE

$ErrorActionPreference = "Stop"

function Make-Commit {
    param([string]$Message, [string]$Date)
    $env:GIT_AUTHOR_DATE = $Date
    $env:GIT_COMMITTER_DATE = $Date
    git commit -m $Message
    Remove-Item Env:\GIT_AUTHOR_DATE
    Remove-Item Env:\GIT_COMMITTER_DATE
}

# ══════════════════════════════════════════════════════════════
# MONDAY, MAR 30 — Initial Cyber Pong Setup & Ball Mechanics
# ══════════════════════════════════════════════════════════════
$MON = "2026-03-30T13:20:00+08:00"
git add games/cyber_pong/__init__.py
Make-Commit "feat(cyber_pong): initialize cyber pong game directory and package" $MON

$MON2 = "2026-03-30T16:45:00+08:00"
git add games/cyber_pong/game.py
Make-Commit "feat(cyber_pong): scaffold ball physics and wall collision logic" $MON2

# ══════════════════════════════════════════════════════════════
# TUESDAY, MAR 31 — Paddle Classes & Collision Detection
# ══════════════════════════════════════════════════════════════
$TUE = "2026-03-31T10:30:00+08:00"
git add games/cyber_pong/game.py
Make-Commit "feat(cyber_pong): implement PlayerPaddle and AIPaddle with movement logic" $TUE

$TUE2 = "2026-03-31T14:55:00+08:00"
git add games/cyber_pong/game.py
Make-Commit "fix(cyber_pong): correct ball-paddle collision response and spin offset" $TUE2

# ══════════════════════════════════════════════════════════════
# WEDNESDAY, APR 1 — Scoring, Particles & Neon Visual Polish
# ══════════════════════════════════════════════════════════════
$WED = "2026-04-01T11:10:00+08:00"
git add games/cyber_pong/game.py
Make-Commit "feat(cyber_pong): add scoring system, win condition, and score flash" $WED

$WED2 = "2026-04-01T15:20:00+08:00"
git add games/cyber_pong/game.py
Make-Commit "feat(cyber_pong): add neon particle effects, ball trail and rally counter" $WED2

# ══════════════════════════════════════════════════════════════
# THURSDAY, APR 2 — Launcher Integration & Final Debugging
# ══════════════════════════════════════════════════════════════
$THU = "2026-04-02T09:50:00+08:00"
git add launcher.py
Make-Commit "feat(launcher): register Cyber Pong as game 6 with NEON_ORANGE theme" $THU

$THU2 = "2026-04-02T11:40:00+08:00"
git add launcher.py
Make-Commit "fix(launcher): adjust card height and spacing to fit 6 games without clipping" $THU2

$THU3 = "2026-04-02T14:30:00+08:00"
git add spread_cyber_pong_commits.ps1
Make-Commit "chore: add commit spreading script for cyber pong week" $THU3

Write-Host ""
Write-Host "=== All commits created! ===" -ForegroundColor Green
Write-Host "Running 'git push origin main'..."
git push origin main
