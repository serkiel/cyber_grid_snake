$ErrorActionPreference = "Stop"

# Create log file for tracking
$LogFile = "spread_operation_apr13_17_log.txt"
"Starting Commit Spread Operation" | Out-File $LogFile

# Target Dates for the week of April 13 - April 17
$date_mon = "2026-04-13T11:15:00"
$date_tue = "2026-04-14T14:30:00"
$date_wed = "2026-04-15T10:45:00"
$date_thu = "2026-04-16T16:20:00"
$date_fri = "2026-04-17T14:15:00"

# MONDAY
Write-Host "Committing MONDAY changes..."
git rm --ignore-unmatch operation_log_mar30_apr2.txt
git add launcher.py game.py
$env:GIT_AUTHOR_DATE=$date_mon; $env:GIT_COMMITTER_DATE=$date_mon
git commit -m "feat: Add full-screen support and dynamic window resize handling"

# TUESDAY
Write-Host "Committing TUESDAY changes..."
git add games/snake/food.py games/snake/renderer.py games/snake/snake.py
$env:GIT_AUTHOR_DATE=$date_tue; $env:GIT_COMMITTER_DATE=$date_tue
git commit -m "style: Refine Snake game visual layouts and entity mechanics"

# WEDNESDAY 
Write-Host "Committing WEDNESDAY changes..."
git add gen_crash_sfx.py gen_eat_sfx.py gen_sfx.py crash.wav eat.wav nav.wav select.wav
$env:GIT_AUTHOR_DATE=$date_wed; $env:GIT_COMMITTER_DATE=$date_wed
git commit -m "feat: Develop synthesized audio generation scripts and baseline wav files"

# THURSDAY
Write-Host "Committing THURSDAY changes..."
git add games/snake/game.py
$env:GIT_AUTHOR_DATE=$date_thu; $env:GIT_COMMITTER_DATE=$date_thu
git commit -m "feat: Integrate sfx logic and fix overhead layout issues in Snake game loop"

# FRIDAY
Write-Host "Committing FRIDAY changes..."
git add games/cyber_breakout/game.py games/cyber_dash/game.py games/cyber_pong/game.py games/data_drop/game.py games/reaction/game.py operation_log_apr13_17.txt
$env:GIT_AUTHOR_DATE=$date_fri; $env:GIT_COMMITTER_DATE=$date_fri
git commit -m "feat: Deploy comprehensive audio feedback systems across remaining games"

# Push to origin
Write-Host "Pushing changes to remote..."
git push origin main

Write-Host "Operation Complete."
"Operation Complete" | Out-File $LogFile -Append
