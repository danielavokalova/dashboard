@echo off
chcp 65001 >nul
title Nastaveni autostartu

REM Pokud je server.py ve stejne slozce, pokracuj
if exist "%~dp0server.py" (
    cd /d "%~dp0"
    goto :setup
)

REM Jinak ho najdi automaticky
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

:setup
REM Vytvor .env pokud neexistuje
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo  Vyplnte udaje k databazi a ulozit.
    notepad .env
    pause
)

REM Nainstaluj zavislosti
python -c "import flask, flask_cors, psycopg2, dotenv" >nul 2>&1
if errorlevel 1 (
    echo  Instaluji zavislosti...
    pip install -r requirements.txt -q
)

set "HERE=%CD%"

REM Vytvor server-silent.vbs pokud chybi
if not exist "%HERE%\server-silent.vbs" (
    echo Dim folder > "%HERE%\server-silent.vbs"
    echo folder = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\")) >> "%HERE%\server-silent.vbs"
    echo CreateObject("WScript.Shell").Run "cmd /c """ ^& folder ^& "start-server.bat""", 0, False >> "%HERE%\server-silent.vbs"
)

REM Pridej do Startupu Windows
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "LINK=%STARTUP%\AirReservationsDashboard.lnk"

powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%LINK%'); $s.TargetPath = '%HERE%\server-silent.vbs'; $s.WorkingDirectory = '%HERE%'; $s.WindowStyle = 0; $s.Description = 'Air Reservations Dashboard'; $s.Save()"

REM Spust server hned ted
start "" "%HERE%\server-silent.vbs"

timeout /t 3 /nobreak >nul
start http://localhost:8080/air-reservations.html

echo.
echo  Hotovo! Server se spousti automaticky s Windows.
echo.
pause
