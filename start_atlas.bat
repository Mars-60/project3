@echo off
title Atlas - Starting...
cd /d "%~dp0"

echo ============================================
echo   Atlas - AI Memory Assistant
echo ============================================
echo.

REM ── Activate the virtual environment first ────────────────────────────────
if not exist "%~dp0venv\Scripts\activate.bat" (
    echo  [ERROR] Virtual environment not found.
    echo          Please run setup.bat first.
    pause
    exit /b 1
)
call "%~dp0venv\Scripts\activate.bat"

echo Starting Atlas... (this window must stay open)
echo.

python "%~dp0start_atlas.py"

echo.
echo Atlas stopped. Press any key to close.
pause > nul
