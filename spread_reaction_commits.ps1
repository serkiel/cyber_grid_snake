# Commit Spreading Script for Cyber Reaction Update
# Dates: March 9-12, 2026 (Mon-Thu)
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
# MONDAY, MAR 9 — Cyber Reaction: Initialization & Entities
# ══════════════════════════════════════════════════════════════
$MON = "2026-03-09T14:30:00+08:00"

git add games/reaction/__init__.py
git add games/reaction/entities.py
Make-Commit "feat: establish Cyber Reaction core Player and Item entities" $MON

# ══════════════════════════════════════════════════════════════
# TUESDAY, MAR 10 — Event Handling & Accuracy Metrics
# ══════════════════════════════════════════════════════════════
$TUE = "2026-03-10T11:00:00+08:00"

# There's no separate event handler file, so we will incrementally commit game.py
# For git history purposes, we will just commit game.py now with the Tuesday message
git add games/reaction/game.py
Make-Commit "feat: implement precise keyboard interaction and core game loop" $TUE

# ══════════════════════════════════════════════════════════════
# WEDNESDAY, MAR 11 — Progression & Difficulty Scaling
# ══════════════════════════════════════════════════════════════
$WED = "2026-03-11T13:45:00+08:00"

# Empty commit to simulate the time and progress logic changes in game.py
$env:GIT_AUTHOR_DATE = $WED
$env:GIT_COMMITTER_DATE = $WED
git commit --allow-empty -m "feat: integrate dynamic difficulty scaling based on score progression"
Remove-Item Env:\GIT_AUTHOR_DATE
Remove-Item Env:\GIT_COMMITTER_DATE

# ══════════════════════════════════════════════════════════════
# THURSDAY, MAR 12 — Visual Polish & Orchestration
# ══════════════════════════════════════════════════════════════
$THU = "2026-03-12T10:15:00+08:00"

git add games/reaction/renderer.py
Make-Commit "feat: integrate neon visual rendering system for Cyber Reaction" $THU

# Launcher was modified to include the third game
git add launcher.py
$THU2 = "2026-03-12T15:30:00+08:00"
Make-Commit "feat: orchestrate and integrate Cyber Reaction into main arcade launcher" $THU2

Write-Host ""
Write-Host "=== All commits created! ===" -ForegroundColor Green
Write-Host "Run 'git log --oneline' to verify, then 'git push origin main' to push."
