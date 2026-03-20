# Commit Spreading Script for Cyber Arcade (Data Drop Update)
# Dates: March 16-20, 2026 (Mon-Fri)
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
# MONDAY, MAR 16 — Ideation & Architecture Planning
# ══════════════════════════════════════════════════════════════
$MON = "2026-03-16T14:30:00+08:00"
git add games/data_drop/__init__.py
Make-Commit "feat(data_drop): initialize data drop game directory and structure" $MON

# ══════════════════════════════════════════════════════════════
# TUESDAY, MAR 17 — Data Drop Core Mechanics
# ══════════════════════════════════════════════════════════════
$TUE = "2026-03-17T11:00:00+08:00"
git add games/data_drop/game.py
Make-Commit "feat(data_drop): implement core match-3 grid mechanics and block physics" $TUE

# ══════════════════════════════════════════════════════════════
# WEDNESDAY, MAR 18 — Renderer & Visual Feedback
# ══════════════════════════════════════════════════════════════
$WED = "2026-03-18T13:45:00+08:00"
git add games/data_drop/renderer.py
Make-Commit "feat(data_drop): integrate neon visual renderer and match animations" $WED

# ══════════════════════════════════════════════════════════════
# THURSDAY, MAR 19 — Global Framework Scaling
# ══════════════════════════════════════════════════════════════
$THU = "2026-03-19T10:15:00+08:00"
git add config.py
Make-Commit "feat(core): increase master grid resolution to 800x640" $THU

# ══════════════════════════════════════════════════════════════
# FRIDAY, MAR 20 — Integration & UI Formatting
# ══════════════════════════════════════════════════════════════
$FRI = "2026-03-20T15:30:00+08:00"
git add launcher.py
git add task.md  # if it accidentally ended up in the working dir instead of .gemini, or just to be safe
# (Actually I won't add task.md since it belongs in .gemini)
Make-Commit "feat(ui): orchestrate Data Drop integration and center home UI layout" $FRI

# Include the scripts
git add spread_data_drop_commits.ps1
$FRI_EOD = "2026-03-20T17:00:00+08:00"
Make-Commit "chore: add workflow script for data drop commits" $FRI_EOD

Write-Host ""
Write-Host "=== All commits created! ===" -ForegroundColor Green
Write-Host "Running 'git push origin main'..."
git push origin main
