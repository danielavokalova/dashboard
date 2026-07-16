@echo off
chcp 65001 >nul
title Air Reservations Dashboard

REM Pokud je server.py ve stejne slozce, spust rovnou
if exist "%~dp0server.py" (
    cd /d "%~dp0"
    goto :run
)

REM Jinak ho najdi automaticky v uzivatelskem profilu
echo  Hledam server.py...
set "FOUND="
for /f "delims=" %%i in ('powershell -NoProfile -Command "Get-ChildItem -Path $env:USERPROFILE -Filter server.py -Recurse -ErrorAction SilentlyContinue | Where-Object { Test-Path (Join-Path $_.DirectoryName \".env.example\") } | Select-Object -First 1 -ExpandProperty DirectoryName"') do set "FOUND=%%i"

if not defined FOUND (
    echo.
    echo  [CHYBA] server.py nebyl nalezen. Ujistete se, ze je repozitar stazen.
    pause
    exit /b 1
)

echo  Nalezeno: %FOUND%
cd /d "%FOUND%"

:run
REM Zkontroluj Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [CHYBA] Python nebyl nalezen. Nainstaluj z https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Vytvor .env pokud neexistuje
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo  [PRVNI SPUSTENI] Vyplnte udaje k databazi a ulozit.
    notepad .env
    pause
)

REM Nainstaluj zavislosti jen pokud jeste nejsou
python -c "import flask, flask_cors, psycopg2, dotenv" >nul 2>&1
if errorlevel 1 (
    echo  Instaluji zavislosti...
    pip install -r requirements.txt -q
)

REM ── Spust Postgres + sync (pokud je Docker dostupny) ──────────
docker start metabase_projekt-postgres-1 >nul 2>&1
docker start google-sync >nul 2>&1
echo  [OK]   Postgres + sync kontrola dokoncena

REM Exportuj aktualni data do lokalniho CSV (zaloha pro staticky rezim)
start "" cmd /c "timeout /t 5 /nobreak >nul && python export_csv.py"

REM ── Otevri prohlizec po startu serveru (?refresh=1 = nacti data) ─
start "" cmd /c "timeout /t 5 /nobreak >nul && start http://localhost:8080/air-reservations.html?refresh=1"

REM Spust server
python server.py

pause
