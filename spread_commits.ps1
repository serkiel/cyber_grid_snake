# Spread commits across 7 days (Feb 21 - Feb 27, 2026)
# Each commit adds a logical piece of the project

# Day 1 (Feb 21): Project init — .gitignore, requirements.txt, README skeleton
$env:GIT_AUTHOR_DATE = "2026-02-21T10:00:00+08:00"
$env:GIT_COMMITTER_DATE = "2026-02-21T10:00:00+08:00"
git add .gitignore requirements.txt
git commit -m "chore: init project with requirements and gitignore"

$env:GIT_AUTHOR_DATE = "2026-02-21T14:30:00+08:00"
$env:GIT_COMMITTER_DATE = "2026-02-21T14:30:00+08:00"
git add README.md
git commit -m "docs: add project README"

# Day 2 (Feb 22): Config and main entry
$env:GIT_AUTHOR_DATE = "2026-02-22T11:00:00+08:00"
$env:GIT_COMMITTER_DATE = "2026-02-22T11:00:00+08:00"
git add config.py
git commit -m "feat: add config with grid, color, and FPS constants"

$env:GIT_AUTHOR_DATE = "2026-02-22T15:00:00+08:00"
$env:GIT_COMMITTER_DATE = "2026-02-22T15:00:00+08:00"
git add main.py
git commit -m "feat: add main entry point"

# Day 3 (Feb 23): Snake entity
$env:GIT_AUTHOR_DATE = "2026-02-23T09:30:00+08:00"
$env:GIT_COMMITTER_DATE = "2026-02-23T09:30:00+08:00"
git add snake.py
git commit -m "feat: add Snake class with direction queue and collision logic"

# Day 4 (Feb 24): Food entity
$env:GIT_AUTHOR_DATE = "2026-02-24T10:00:00+08:00"
$env:GIT_COMMITTER_DATE = "2026-02-24T10:00:00+08:00"
git add food.py
git commit -m "feat: add Food class with random spawn and pulse animation"

# Day 5 (Feb 25): Grid renderer
$env:GIT_AUTHOR_DATE = "2026-02-25T11:00:00+08:00"
$env:GIT_COMMITTER_DATE = "2026-02-25T11:00:00+08:00"
git add grid_renderer.py
git commit -m "feat: add GridRenderer with neon grid, glow effects, and UI overlays"

# Day 6 (Feb 26): Game controller
$env:GIT_AUTHOR_DATE = "2026-02-26T10:00:00+08:00"
$env:GIT_COMMITTER_DATE = "2026-02-26T10:00:00+08:00"
git add game.py
git commit -m "feat: add Game class with state machine, WASD, pause, and high score"

# Day 7 (today Feb 27): Final polish
$env:GIT_AUTHOR_DATE = "2026-02-27T13:00:00+08:00"
$env:GIT_COMMITTER_DATE = "2026-02-27T13:00:00+08:00"
# Stage any remaining files
git add -A
git commit -m "polish: finalize game with title screen, pulsing food, and styled HUD" --allow-empty

# Clean up env vars
Remove-Item Env:\GIT_AUTHOR_DATE
Remove-Item Env:\GIT_COMMITTER_DATE

Write-Host ""
Write-Host "=== All commits created! ===" -ForegroundColor Green
Write-Host "Run 'git log --oneline' to verify, then push with:"
Write-Host "  git remote add origin https://github.com/serkiel/cyber_grid_snake.git"
Write-Host "  git branch -M main"
Write-Host "  git push -u origin main"
