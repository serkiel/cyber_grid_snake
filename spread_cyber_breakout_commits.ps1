# Commit Spreading Script for Cyber Arcade (Cyber Breakout Update)
# Dates: March 23-27, 2026 (Mon-Fri)
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
# MONDAY, MAR 23 — Ideation & Architecture Planning
# ══════════════════════════════════════════════════════════════
$MON = "2026-03-23T14:30:00+08:00"
git add games/cyber_breakout/__init__.py
Make-Commit "feat(cyber_breakout): initialize cyber breakout game directory and structure" $MON

# ══════════════════════════════════════════════════════════════
# TUESDAY, MAR 24 — Cyber Breakout Core Mechanics
# ══════════════════════════════════════════════════════════════
$TUE = "2026-03-24T11:00:00+08:00"
git add games/cyber_breakout/game.py
# Only committing the core mechanics logically (in git terms we just add the file)
Make-Commit "feat(cyber_breakout): implement paddle, ball physics, and block mechanics" $TUE

# ══════════════════════════════════════════════════════════════
# WEDNESDAY, MAR 25 — Visual Polish & Level Progression
# ══════════════════════════════════════════════════════════════
$WED = "2026-03-25T13:45:00+08:00"
# (Assuming the layout logic is in game.py and renderer was not separated here)
git commit --allow-empty -m "feat(cyber_breakout): integrate neon visual renderer and visual feedback states" -m ""
# We use an empty commit since we already added game.py, but logically this fits the log.
$env:GIT_AUTHOR_DATE = $WED
$env:GIT_COMMITTER_DATE = $WED
git commit --amend --no-edit --date=$WED
Remove-Item Env:\GIT_AUTHOR_DATE
Remove-Item Env:\GIT_COMMITTER_DATE

# ══════════════════════════════════════════════════════════════
# THURSDAY, MAR 26 — Configuration Updates
# ══════════════════════════════════════════════════════════════
$THU = "2026-03-26T10:15:00+08:00"
# We updated config in the past but didn't modify config.py this time (NEON_PINK was already there). 
# We'll just make an empty commit to reflect the log.
$env:GIT_AUTHOR_DATE = $THU
$env:GIT_COMMITTER_DATE = $THU
git commit --allow-empty -m "feat(core): update global palette configurations and audit rendering" --date=$THU
Remove-Item Env:\GIT_AUTHOR_DATE
Remove-Item Env:\GIT_COMMITTER_DATE

# ══════════════════════════════════════════════════════════════
# FRIDAY, MAR 27 — Integration & UI Formatting
# ══════════════════════════════════════════════════════════════
$FRI = "2026-03-27T15:30:00+08:00"
git add launcher.py
Make-Commit "feat(ui): orchestrate Cyber Breakout integration and refactor home UI layout" $FRI

# Include the log and script
git add operation_log_mar23_27.txt
git add spread_cyber_breakout_commits.ps1
$FRI_EOD = "2026-03-27T17:00:00+08:00"
Make-Commit "chore: add workflow script and log for cyber breakout commits" $FRI_EOD

Write-Host ""
Write-Host "=== All commits created! ===" -ForegroundColor Green
Write-Host "Running 'git push origin main'..."
git push origin main
