@echo off
title Atlas - Starting...
cd /d "%~dp0"

echo ============================================
echo   Atlas - AI Memory Assistant
echo ============================================
echo.
echo Starting Atlas... (this window must stay open)
echo.

python start_atlas.py

echo.
echo Atlas stopped. Press any key to close.
pause > nul