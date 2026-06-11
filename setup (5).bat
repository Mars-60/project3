@echo off
title Atlas - First Time Setup
color 0A

REM Store project directory immediately — works even with spaces in path
set "ATLAS_DIR=%~dp0"
if "%ATLAS_DIR:~-1%"=="\" set "ATLAS_DIR=%ATLAS_DIR:~0,-1%"

echo.
echo  ==========================================
echo   Atlas - AI Memory Assistant
echo   First Time Setup
echo  ==========================================
echo.

REM ── Check Python ──────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed.
    echo.
    echo  Please install Python 3.10 or higher from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: Check "Add Python to PATH" during install.
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)
echo  [OK] Python found.

REM ── Check pip ─────────────────────────────────────────────────────────────
pip --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] pip not found. Please reinstall Python.
    pause
    exit /b 1
)

REM ── Create virtual environment ────────────────────────────────────────────
echo.
echo  [1/5] Creating virtual environment...
if not exist "%ATLAS_DIR%\venv" (
    python -m venv "%ATLAS_DIR%\venv"
    echo  [OK] Virtual environment created.
) else (
    echo  [OK] Virtual environment already exists.
)

REM ── Activate venv ─────────────────────────────────────────────────────────
call "%ATLAS_DIR%\venv\Scripts\activate.bat"

REM ── Install dependencies ──────────────────────────────────────────────────
echo.
echo  [2/5] Installing Python packages...
echo  (This may take 2-3 minutes on first run)
pip install -r "%ATLAS_DIR%\requirements.txt" --quiet
if errorlevel 1 (
    echo  [ERROR] Failed to install packages. Check your internet connection.
    pause
    exit /b 1
)
echo  [OK] Packages installed.

REM ── Check Tesseract ───────────────────────────────────────────────────────
echo.
echo  [3/5] Checking Tesseract OCR...
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo  [OK] Tesseract found.
) else (
    echo  [!] Tesseract OCR not found.
    echo.
    echo  Please install it from:
    echo  https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo  Install to: C:\Program Files\Tesseract-OCR\
    echo.
    echo  Opening download page...
    start https://github.com/UB-Mannheim/tesseract/wiki
    echo  After installing Tesseract, run this setup again.
    pause
    exit /b 1
)

REM ── Gemini API Key ────────────────────────────────────────────────────────
echo.
echo  [4/5] Setting up Gemini API Key...

if exist "%ATLAS_DIR%\.env" (
    findstr /C:"GEMINI_API_KEY" "%ATLAS_DIR%\.env" >nul 2>&1
    if not errorlevel 1 (
        echo  [OK] API key already configured.
        goto api_done
    )
)

echo.
echo  You need a FREE Gemini API key from Google.
echo.
echo  Steps:
echo  1. Go to: https://aistudio.google.com/app/apikey
echo  2. Sign in with your Google account
echo  3. Click "Create API Key"
echo  4. Copy the key and paste it below
echo.
start https://aistudio.google.com/app/apikey
echo.
set /p GEMINI_KEY="  Paste your Gemini API key here: "

if "%GEMINI_KEY%"=="" (
    echo  [ERROR] No API key entered. Please run setup again.
    pause
    exit /b 1
)

echo GEMINI_API_KEY=%GEMINI_KEY% > "%ATLAS_DIR%\.env"
echo  [OK] API key saved to .env file.

:api_done

REM ── Initialize database ───────────────────────────────────────────────────
echo.
echo  [5/5] Initializing database...
python "%ATLAS_DIR%\init_db.py"

REM ── Install Chrome Extension ──────────────────────────────────────────────
echo.
echo  ==========================================
echo   LAST STEP: Install Chrome Extension
echo  ==========================================
echo.
echo  1. Open Chrome and go to: chrome://extensions
echo  2. Enable "Developer mode" (top right toggle)
echo  3. Click "Load unpacked"
echo  4. Select the "extension" folder inside this project
echo.
echo  This lets Atlas track your browser activity.
echo.
set /p OPEN_CHROME="  Open Chrome extensions page now? (Y/N): "
if /i "%OPEN_CHROME%"=="Y" start chrome chrome://extensions

REM ── Auto-start on login ───────────────────────────────────────────────────
echo.
echo  ==========================================
echo   Auto-Start on Login
echo  ==========================================
echo.
echo  Would you like Atlas to start automatically
echo  every time you log into Windows?
echo.
echo  (It will run silently in the background.)
echo.
set /p AUTO_START="  Enable auto-start on login? (Y/N): "

if /i "%AUTO_START%"=="Y" (
    goto do_autostart
) else (
    echo  [OK] Skipped. Run install_autostart.bat anytime to enable it.
    goto setup_done
)

:do_autostart
REM -- Write VBScript silent launcher (no console window on login)
set "LAUNCHER=%ATLAS_DIR%\atlas_silent_launch.vbs"
echo Set WshShell = CreateObject("WScript.Shell") > "%LAUNCHER%"
echo WshShell.Run Chr(34) ^& "%ATLAS_DIR%\Start_Atlas.bat" ^& Chr(34), 0, False >> "%LAUNCHER%"

REM -- Register via PowerShell Task Scheduler (handles spaces in paths, no UAC prompt)
set "PS_TASK=%TEMP%\atlas_task.ps1"
(
    echo $AtlasDir = '%ATLAS_DIR%'
    echo $VbsPath  = "$AtlasDir\atlas_silent_launch.vbs"
    echo $action   = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$VbsPath`""
    echo $trigger  = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
    echo $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ^(New-TimeSpan -Hours 0^) -RestartCount 3 -RestartInterval ^(New-TimeSpan -Minutes 1^) -StartWhenAvailable $true
    echo Register-ScheduledTask -TaskName "AtlasAutoStart" -Action $action -Trigger $trigger -Settings $settings -RunLevel Limited -Force
) > "%PS_TASK%"

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_TASK%" >nul 2>&1
del "%PS_TASK%" >nul 2>&1

REM -- Verify registration
schtasks /query /tn "AtlasAutoStart" >nul 2>&1
if not errorlevel 1 (
    echo  [OK] Auto-start ENABLED. Atlas will start silently on every login.
    echo       No permission prompts. No console window.
    goto setup_done
)

REM -- Fallback: Startup Folder shortcut
echo  [!] Task Scheduler needs Admin rights. Using Startup Folder as fallback...
set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Atlas.lnk"
set "PS2=%TEMP%\atlas_lnk.ps1"
echo $ws = New-Object -ComObject WScript.Shell > "%PS2%"
echo $s = $ws.CreateShortcut('%SHORTCUT%') >> "%PS2%"
echo $s.TargetPath = '%ATLAS_DIR%\Start_Atlas.bat' >> "%PS2%"
echo $s.WorkingDirectory = '%ATLAS_DIR%' >> "%PS2%"
echo $s.WindowStyle = 7 >> "%PS2%"
echo $s.Save() >> "%PS2%"
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS2%"
del "%PS2%" >nul 2>&1

if exist "%SHORTCUT%" (
    echo  [OK] Auto-start ENABLED via Startup Folder.
    echo  [!] You may see a permission prompt on first login - this is normal.
    echo      To remove it: run setup.bat as Administrator next time.
) else (
    echo  [ERROR] Auto-start could not be set up automatically.
    echo          Right-click setup.bat and choose "Run as Administrator".
)

:setup_done
echo.
echo  ==========================================
echo   Setup Complete!
echo  ==========================================
echo.
echo  To start Atlas manually, double-click: Start_Atlas.bat
echo.
pause