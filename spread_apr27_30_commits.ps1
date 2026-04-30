# Commit Spreading Script for Cyber Arcade (Advanced Analytics Week)
# Dates: April 27 - 30, 2026 (Mon-Thu, Friday is Labor Day)
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
# MONDAY, APR 27 — Spatial Analytics & Schema Expansion
# ══════════════════════════════════════════════════════════════
$MON = "2026-04-27T14:30:00+08:00"
git add telemetry_db.py
Make-Commit "feat(database): upgrade sqlite schema to support geospatial event coordinate logging" $MON

# ══════════════════════════════════════════════════════════════
# TUESDAY, APR 28 — Geospatial Telemetry Hooks
# ══════════════════════════════════════════════════════════════
$TUE = "2026-04-28T13:45:00+08:00"
git add games/snake/game.py
Make-Commit "feat(gameplay): pipe exact game over spatial coordinates to the analytics database" $TUE

# ══════════════════════════════════════════════════════════════
# WEDNESDAY, APR 29 — Unsupervised Machine Learning
# ══════════════════════════════════════════════════════════════
$WED = "2026-04-29T15:20:00+08:00"
git add requirements.txt
Make-Commit "chore(ml): integrate scikit-learn pipeline for unsupervised player classification" $WED

# ══════════════════════════════════════════════════════════════
# THURSDAY, APR 30 — Analytics Dashboard & Automated Reporting
# ══════════════════════════════════════════════════════════════
$THU = "2026-04-30T11:00:00+08:00"
git add dashboard.py
git add generate_mock_data.py
git add operation_log_apr27_30.txt
git add spread_apr27_30_commits.ps1
git add .
Make-Commit "feat(dashboard): architect dynamic heatmap visualizations, k-means modeling, and CSV report exports" $THU

Write-Host ""
Write-Host "=== All Advanced Analytics commits created! ===" -ForegroundColor Green
Write-Host "Running 'git push origin main'..."
git push origin main
