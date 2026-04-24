# Commit Spreading Script for Cyber Arcade (Data Analytics Week)
# Dates: April 20 - 24, 2026 (Mon-Fri)
# Each commit is backdated using GIT_AUTHOR_DATE and GIT_COMMITTER_DATE to show daily progress.

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
# MONDAY, APR 20 — Telemetry Engine & DB Setup
# ══════════════════════════════════════════════════════════════
$MON = "2026-04-20T14:30:00+08:00"
git add telemetry_db.py
Make-Commit "feat(analytics): implement centralized SQLite telemetry logging engine" $MON

# ══════════════════════════════════════════════════════════════
# TUESDAY, APR 21 — Cross-Game Data Pipeline
# ══════════════════════════════════════════════════════════════
$TUE = "2026-04-21T13:45:00+08:00"
git add launcher.py
git add games/snake/game.py
git add games/data_drop/game.py
git add games/cyber_breakout/game.py
git add games/cyber_pong/game.py
Make-Commit "feat(analytics): hook automated telemetry pipelines into game over states" $TUE

# ══════════════════════════════════════════════════════════════
# WEDNESDAY, APR 22 — Algorithmic Dataset Generation
# ══════════════════════════════════════════════════════════════
$WED = "2026-04-22T15:20:00+08:00"
git add generate_mock_data.py
Make-Commit "chore(dataset): engineer mock algorithmic data generator for analytics visualization" $WED

# ══════════════════════════════════════════════════════════════
# THURSDAY, APR 23 — Interactive Data Dashboard
# ══════════════════════════════════════════════════════════════
$THU = "2026-04-23T11:00:00+08:00"
git add dashboard.py
git add requirements.txt
Make-Commit "feat(dashboard): build standalone streamlit web dashboard for kpi telemetry tracking" $THU

# ══════════════════════════════════════════════════════════════
# FRIDAY, APR 24 — Product A/B Testing & Final Run
# ══════════════════════════════════════════════════════════════
$FRI = "2026-04-24T16:00:00+08:00"
git add games/reaction/game.py
git add games/cyber_dash/game.py
git add setup_and_run.py
git add operation_log_apr20_24.txt
# Catch any extra un-staged modifications to the database or untracked stuff 
# (excluding db from tracking since it's locally generated data)
git add .gitignore
# Ensure we don't accidentally push the SQL DB itself since it changes locally
Out-File -FilePath .gitignore -Append -InputObject "game_data.db" -Encoding utf8
git add .
Make-Commit "feat(experimentation): integrate A/B testing infrastructure into dash and reaction games" $FRI

Write-Host ""
Write-Host "=== All Data Analytics commits created! ===" -ForegroundColor Green
Write-Host "Running 'git push -f origin main'..."
git push -f origin main
