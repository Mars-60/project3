@echo off
title Atlas - Auto-Start Manager
color 0A

REM ── Silent mode: called from setup.bat with "silent" argument ─────────────
if /i "%1"=="silent" goto enable

echo.
echo  ==========================================
echo   Atlas - Auto-Start Manager
echo  ==========================================
echo.
echo  What would you like to do?
echo.
echo  [1] Enable  - Start Atlas automatically on login
echo  [2] Disable - Remove Atlas from auto-start
echo  [3] Status  - Check if auto-start is active
echo  [4] Exit
echo.
set /p CHOICE="  Enter choice (1/2/3/4): "

if "%CHOICE%"=="1" goto enable
if "%CHOICE%"=="2" goto disable
if "%CHOICE%"=="3" goto status
if "%CHOICE%"=="4" exit /b 0

echo  [ERROR] Invalid choice.
pause
exit /b 1


REM ════════════════════════════════════════════════════════════════════════════
:enable
REM ════════════════════════════════════════════════════════════════════════════

set "ATLAS_DIR=%~dp0"
if "%ATLAS_DIR:~-1%"=="\" set "ATLAS_DIR=%ATLAS_DIR:~0,-1%"

REM Verify Start_Atlas.bat exists in this folder
if not exist "%ATLAS_DIR%\Start_Atlas.bat" (
    echo.
    echo  [ERROR] Start_Atlas.bat not found in:
    echo          %ATLAS_DIR%
    echo          Make sure you are running this from inside the Atlas project folder.
    if not "%1"=="silent" pause
    exit /b 1
)

REM Write the VBScript silent launcher (suppresses console window on login)
set "LAUNCHER=%ATLAS_DIR%\atlas_silent_launch.vbs"
(
    echo Set WshShell = CreateObject("WScript.Shell"^)
    echo WshShell.Run Chr(34^) ^& "%ATLAS_DIR%\Start_Atlas.bat" ^& Chr(34^), 0, False
) > "%LAUNCHER%"

REM Register with Task Scheduler (all on ONE line — no ^ continuation inside subroutine)
schtasks /create /tn "AtlasAutoStart" /tr "wscript.exe \"%LAUNCHER%\"" /sc ONLOGON /rl LIMITED /f >nul 2>&1

if errorlevel 1 (
    echo.
    echo  [!] Task Scheduler failed. Trying Startup Folder instead...
    goto try_startup_folder
)

echo.
echo  [OK] Auto-start ENABLED via Task Scheduler.
echo       Atlas will launch silently on every login.
if not "%1"=="silent" pause
exit /b 0

:try_startup_folder
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP%\Atlas.lnk"

REM Write a PowerShell script to a temp file to avoid escaping issues
set "PS_SCRIPT=%TEMP%\atlas_shortcut.ps1"
(
    echo $ws = New-Object -ComObject WScript.Shell
    echo $s = $ws.CreateShortcut('%SHORTCUT%')
    echo $s.TargetPath = '%ATLAS_DIR%\Start_Atlas.bat'
    echo $s.WorkingDirectory = '%ATLAS_DIR%'
    echo $s.WindowStyle = 7
    echo $s.Description = 'Atlas AI Memory Assistant'
    echo $s.Save()
) > "%PS_SCRIPT%"

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%"
del "%PS_SCRIPT%" >nul 2>&1

if exist "%SHORTCUT%" (
    echo  [OK] Auto-start ENABLED via Startup Folder.
) else (
    echo  [ERROR] Both methods failed.
    echo          Run this file as Administrator, or follow manual steps:
    call :write_manual_instructions
    echo          Instructions saved to: MANUAL_AUTOSTART.txt
)

if not "%1"=="silent" pause
exit /b 0


REM ════════════════════════════════════════════════════════════════════════════
:disable
REM ════════════════════════════════════════════════════════════════════════════

set "ATLAS_DIR=%~dp0"
if "%ATLAS_DIR:~-1%"=="\" set "ATLAS_DIR=%ATLAS_DIR:~0,-1%"
set "REMOVED=0"

schtasks /query /tn "AtlasAutoStart" >nul 2>&1
if not errorlevel 1 (
    schtasks /delete /tn "AtlasAutoStart" /f >nul 2>&1
    echo  [OK] Removed from Task Scheduler.
    set "REMOVED=1"
)

set "STARTUP_LNK=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Atlas.lnk"
if exist "%STARTUP_LNK%" (
    del "%STARTUP_LNK%" >nul 2>&1
    echo  [OK] Removed from Startup Folder.
    set "REMOVED=1"
)

if exist "%ATLAS_DIR%\atlas_silent_launch.vbs" del "%ATLAS_DIR%\atlas_silent_launch.vbs" >nul 2>&1

if "%REMOVED%"=="0" (
    echo.
    echo  [INFO] Atlas was not set to auto-start. Nothing to remove.
) else (
    echo.
    echo  [OK] Auto-start DISABLED. Atlas will no longer start on login.
)

echo.
pause
exit /b 0


REM ════════════════════════════════════════════════════════════════════════════
:status
REM ════════════════════════════════════════════════════════════════════════════

echo.
set "FOUND=0"

schtasks /query /tn "AtlasAutoStart" >nul 2>&1
if not errorlevel 1 (
    echo  [ACTIVE] Task Scheduler: AtlasAutoStart is registered.
    set "FOUND=1"
) else (
    echo  [--]     Task Scheduler: not registered.
)

set "STARTUP_LNK=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Atlas.lnk"
if exist "%STARTUP_LNK%" (
    echo  [ACTIVE] Startup Folder: Atlas.lnk found.
    set "FOUND=1"
) else (
    echo  [--]     Startup Folder: no shortcut found.
)

echo.
if "%FOUND%"=="1" (
    echo  Result: Atlas IS set to auto-start on login.
) else (
    echo  Result: Atlas is NOT set to auto-start on login.
)

echo.
pause
exit /b 0


REM ════════════════════════════════════════════════════════════════════════════
:write_manual_instructions
REM ════════════════════════════════════════════════════════════════════════════

set "ATLAS_DIR=%~dp0"
if "%ATLAS_DIR:~-1%"=="\" set "ATLAS_DIR=%ATLAS_DIR:~0,-1%"

(
    echo HOW TO MAKE ATLAS START ON LOGIN (MANUAL STEPS)
    echo ================================================
    echo.
    echo Option A - Startup Folder (easiest, 1 minute):
    echo  1. Press Win+R, type:  shell:startup  and press Enter
    echo  2. Right-click inside the folder, New - Shortcut
    echo  3. Browse to Start_Atlas.bat in your Atlas folder
    echo  4. Done. Atlas will start every time you log in.
    echo.
    echo Option B - Task Scheduler (cleaner, no console window):
    echo  1. Press Win+S, search "Task Scheduler", open it
    echo  2. Click "Create Basic Task"
    echo  3. Name: AtlasAutoStart
    echo  4. Trigger: When I log on
    echo  5. Action: Start a program
    echo  6. Program/script:  wscript.exe
    echo  7. Arguments:  "%ATLAS_DIR%\atlas_silent_launch.vbs"
    echo  8. Click Finish
    echo.
    echo To REMOVE auto-start later:
    echo  Option A: Delete Atlas.lnk from the Startup folder
    echo  Option B: Open Task Scheduler, find AtlasAutoStart, right-click Delete
    echo     OR run:  schtasks /delete /tn "AtlasAutoStart" /f
) > "%ATLAS_DIR%\MANUAL_AUTOSTART.txt"

exit /b 0
