@echo off
chcp 65001 >nul
title Nastaveni autostartu

REM Pokud je server.py ve stejne slozce, pokracuj
if exist "%~dp0server.py" cd /d "%~dp0"

REM Jinak ho najdi automaticky
if not exist "server.py" (
    echo  Hledam server.py...
    for /f "delims=" %%i in ('powershell -NoProfile -Command "Get-ChildItem -Path $env:USERPROFILE -Filter server.py -Recurse -ErrorAction SilentlyContinue | Where-Object { Test-Path (Join-Path $_.DirectoryName '.env.example') } | Select-Object -First 1 -ExpandProperty DirectoryName"') do cd /d "%%i"
)

if not exist "server.py" (
    echo  [CHYBA] server.py nebyl nalezen.
    pause
    exit /b 1
)

echo  Slozka: %CD%

REM Stahni nejnovejsi soubory z GitHubu
echo  Stahuji nejnovejsi soubory...
git branch --set-upstream-to=origin/main main >nul 2>&1
git pull origin main >nul 2>&1
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/danielavokalova/dashboard/main/start-server.bat' -OutFile 'start-server.bat'" >nul 2>&1
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/danielavokalova/dashboard/main/export_csv.py' -OutFile 'export_csv.py'" >nul 2>&1
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/danielavokalova/dashboard/main/server.py' -OutFile 'server.py'" >nul 2>&1

REM Vytvor .env pokud neexistuje
if not exist ".env" copy ".env.example" ".env" >nul

REM Nainstaluj zavislosti
python -c "import flask, flask_cors, psycopg2, dotenv" >nul 2>&1
if errorlevel 1 (
    echo  Instaluji zavislosti...
    pip install -r requirements.txt -q
)

REM Vytvor server-silent.vbs
set "VBS=%CD%\server-silent.vbs"
echo Dim folder > "%VBS%"
echo folder = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\")) >> "%VBS%"
echo CreateObject("WScript.Shell"^).Run "cmd /c """ ^& folder ^& "start-server.bat""", 0, False >> "%VBS%"

REM Pridej do Startupu Windows
set "LINK=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\AirReservationsDashboard.lnk"
powershell -NoProfile -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut('%LINK%'); $s.TargetPath='%CD%\server-silent.vbs'; $s.WorkingDirectory='%CD%'; $s.WindowStyle=0; $s.Save()"

REM Spust server
echo  Spoustim server...
start "" "%CD%\server-silent.vbs"

REM Otevri dashboard po 5 sekundach
timeout /t 5 /nobreak >nul
start http://localhost:8080/air-reservations.html

echo.
echo  Hotovo! Server se spousti automaticky s Windows.
echo  Dashboard: http://localhost:8080/air-reservations.html
echo.
pause
