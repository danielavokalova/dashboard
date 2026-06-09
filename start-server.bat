@echo off
chcp 65001 >nul
title Air Reservations Dashboard
cd /d "%~dp0"

REM Zkontroluj ze jsme ve spravne slozce
if not exist "server.py" (
    echo.
    echo  [CHYBA] Soubor server.py nebyl nalezen v teto slozce.
    echo  Uloz vsechny soubory do jedne spolecne slozky a spust bat znovu.
    echo  Stazene soubory: start-server.bat, install-autostart.bat, export_csv.py
    echo  Ostatni soubory jsou v repozitari na GitHubu.
    echo.
    pause
    exit /b 1
)

REM Zkontroluj Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [CHYBA] Python nebyl nalezen.
    echo  Nainstaluj Python z https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Vytvor .env pokud neexistuje
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo  [PRVNI SPUSTENI] Vyplnte prihlasovaci udaje k databazi a ulozit soubor.
    notepad .env
    pause
)

REM Nainstaluj zavislosti jen pokud jeste nejsou
python -c "import flask, flask_cors, psycopg2, dotenv" >nul 2>&1
if errorlevel 1 (
    echo  [INFO] Instaluji zavislosti...
    pip install -r requirements.txt -q
)

REM Spust Docker kontejnery
docker start metabase_projekt-postgres-1 >nul 2>&1
docker start google-sync >nul 2>&1

REM Exportuj aktualni data z DB do CSV a pushni na GitHub
echo  [DATA] Exportuji aktualni data z databaze...
start "" cmd /c "timeout /t 5 /nobreak >nul && python export_csv.py"

REM Otevri prohlizec za 2 sekundy
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8080/air-reservations.html"

REM Spust server
python server.py

pause
