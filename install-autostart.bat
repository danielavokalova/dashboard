@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM Zkontroluj ze jsme ve spravne slozce
if not exist "server.py" (
    echo.
    echo  [CHYBA] Soubor server.py nebyl nalezen.
    echo  Tento soubor musi byt ve stejne slozce jako server.py a ostatni soubory.
    echo  Stahni cely repozitar z GitHubu nebo presun soubory do spravne slozky.
    echo.
    pause
    exit /b 1
)

REM Vytvor .env pokud neexistuje
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo  Vyplnte prihlasovaci udaje k databazi a ulozit soubor.
    notepad .env
    pause
)

REM Nainstaluj zavislosti
python -c "import flask, flask_cors, psycopg2, dotenv" >nul 2>&1
if errorlevel 1 (
    echo  Instaluji zavislosti...
    pip install -r requirements.txt -q
)

REM Pridej server do Startupu Windows
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "LINK=%STARTUP%\AirReservationsDashboard.lnk"

powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%LINK%'); $s.TargetPath = '%~dp0server-silent.vbs'; $s.WorkingDirectory = '%~dp0'; $s.WindowStyle = 0; $s.Description = 'Air Reservations Dashboard'; $s.Save()"

REM Spust server hned ted
start "" "%~dp0server-silent.vbs"

REM Otevri dashboard v prohlizeci
timeout /t 3 /nobreak >nul
start http://localhost:8080/air-reservations.html

echo.
echo  Hotovo! Dashboard se otevrel v prohlizeci.
echo  Od ted se server spousti automaticky s Windows.
echo.
pause
