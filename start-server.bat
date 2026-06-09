@echo off
chcp 65001 >nul
title Air Reservations Dashboard
cd /d "%~dp0"

REM ── Zkontroluj Python ───────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [CHYBA] Python nebyl nalezen.
    echo  Nainstaluj Python z https://www.python.org/downloads/
    pause
    exit /b 1
)

REM ── Vytvoř .env pokud neexistuje ────────────────────────────────
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo  [PRVNÍ SPUŠTĚNÍ] Vyplň přihlašovací údaje k databázi a ulož soubor.
    notepad .env
)

REM ── Nainstaluj závislosti jen pokud ještě nejsou ─────────────────
python -c "import flask, flask_cors, psycopg2, dotenv" >nul 2>&1
if errorlevel 1 (
    echo  [INFO] Instaluji závislosti (jen jednou)...
    pip install -r requirements.txt -q
)

REM ── Spusť Docker kontejnery (pokud jsou dostupné) ────────────────
docker start metabase_projekt-postgres-1 >nul 2>&1
docker start google-sync >nul 2>&1

REM ── Otevři prohlížeč za 2 sekundy ────────────────────────────────
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8080/air-reservations.html"

REM ── Spusť server ─────────────────────────────────────────────────
python server.py

pause
