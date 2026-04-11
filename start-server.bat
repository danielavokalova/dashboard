@echo off
chcp 65001 >nul
title Air Reservations Dashboard
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║         Air Reservations Dashboard               ║
echo  ╚══════════════════════════════════════════════════╝
echo.

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
    echo  [INFO] Soubor .env nenalezen – kopíruji z .env.example
    copy ".env.example" ".env" >nul
    echo.
    echo  ┌─────────────────────────────────────────────────────┐
    echo  │  PRVNÍ SPUŠTĚNÍ – je potřeba nastavit připojení k DB│
    echo  │                                                     │
    echo  │  Otevře se .env – vyplň DB_PASSWORD (a případně    │
    echo  │  DB_NAME / DB_USER) stejně jako má Metabase.        │
    echo  │                                                     │
    echo  │  Ulož soubor a zavři Poznámkový blok,              │
    echo  │  pak se server spustí automaticky.                  │
    echo  └─────────────────────────────────────────────────────┘
    echo.
    notepad .env
)

REM ── Nainstaluj závislosti ────────────────────────────────────────
echo  [1/2] Instaluji Python závislosti...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo  [CHYBA] Instalace závislostí selhala.
    pause
    exit /b 1
)

REM ── Spusť Docker kontejner google-sync (pokud je dostupný) ──────
docker start google-sync >nul 2>&1
if not errorlevel 1 (
    echo  [OK]   Docker kontejner google-sync spuštěn
) else (
    echo  [INFO] Docker kontejner google-sync nebyl nalezen nebo již běží
)

REM ── Otevři prohlížeč po 2 sekundách ────────────────────────────
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8080/air-reservations.html"

echo.
echo  [2/2] Spouštím server → http://localhost:8080/air-reservations.html
echo.
echo  (Zavřením tohoto okna server zastavíš)
echo.

python server.py

pause
