@echo off
chcp 65001 >nul
title Air Reservations - spousteni

REM Spoustec ze webu / ze Stazenych souboru -> vzdy najdi projekt na Desktopu
set "DASH=%USERPROFILE%\Desktop\dashboard"

if not exist "%DASH%\server.py" (
    echo.
    echo  [CHYBA] Projekt dashboard neni ve slozce:
    echo  %DASH%
    echo.
    echo  Zkontroluj, ze mas slozku dashboard na Plose.
    echo.
    pause
    exit /b 1
)

cd /d "%DASH%"
call start-server.bat
