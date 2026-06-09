@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM ── Vytvoř .env pokud neexistuje ──────────────────────────────────
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo  Vyplň přihlašovací údaje k databázi a ulož soubor.
    notepad .env
)

REM ── Nainstaluj závislosti ─────────────────────────────────────────
python -c "import flask, flask_cors, psycopg2, dotenv" >nul 2>&1
if errorlevel 1 (
    echo  Instaluji závislosti...
    pip install -r requirements.txt -q
)

REM ── Přidej server do Startupu Windows ────────────────────────────
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "LINK=%STARTUP%\AirReservationsDashboard.lnk"

powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%LINK%'); $s.TargetPath = '%~dp0server-silent.vbs'; $s.WorkingDirectory = '%~dp0'; $s.WindowStyle = 0; $s.Description = 'Air Reservations Dashboard'; $s.Save()"

REM ── Spusť server hned teď (poprvé) ───────────────────────────────
start "" "%~dp0server-silent.vbs"

REM ── Otevři dashboard v prohlížeči ────────────────────────────────
timeout /t 3 /nobreak >nul
start http://localhost:8080/air-reservations.html

echo.
echo  Hotovo! Dashboard se otevřel v prohlížeči.
echo  Od teď se server spouští automaticky s Windows.
echo  Pro odebrání spusť: remove-autostart.bat
echo.
pause
