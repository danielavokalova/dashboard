@echo off
chcp 65001 >nul
title Nastaveni autostartu

REM Pokud je server.py ve stejne slozce, pokracuj
if exist "%~dp0server.py" (
    cd /d "%~dp0"
    goto :update
)

REM Jinak ho najdi automaticky
echo  Hledam server.py...
set "FOUND="
for /f "delims=" %%i in ('powershell -NoProfile -Command "Get-ChildItem -Path $env:USERPROFILE -Filter server.py -Recurse -ErrorAction SilentlyContinue | Where-Object { Test-Path (Join-Path $_.DirectoryName \".env.example\") } | Select-Object -First 1 -ExpandProperty DirectoryName"') do set "FOUND=%%i"

if not defined FOUND (
    echo.
    echo  [CHYBA] server.py nebyl nalezen.
    pause
    exit /b 1
)

echo  Nalezeno: %FOUND%
cd /d "%FOUND%"

:update
REM Stahni nejnovejsi soubory z GitHubu
echo  Stahuji nejnovejsi soubory...
git branch --set-upstream-to=origin/main main >nul 2>&1
git pull origin main >nul 2>&1

REM Stahni start-server.bat znovu primo z GitHubu (pro jistotu)
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/danielavokalova/dashboard/main/start-server.bat' -OutFile 'start-server.bat'" >nul 2>&1
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/danielavokalova/dashboard/main/export_csv.py' -OutFile 'export_csv.py'" >nul 2>&1

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
echo  Spoustim server...
start "" "%HERE%\server-silent.vbs"

REM Exportuj aktualni data z DB a pushni na GitHub Pages
echo  Exportuji aktualni data na web (chvili potrva)...
timeout /t 6 /nobreak >nul
python export_csv.py

echo.
echo  Oteviram dashboard...
start http://localhost:8080/air-reservations.html
start https://danielavokalova.github.io/dashboard/air-reservations.html

echo.
echo  Hotovo! Data jsou aktualni na obou adresach.
echo  Server se spousti automaticky s Windows.
echo.
pause
