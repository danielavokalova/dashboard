@echo off
chcp 65001 >nul
title Air Reservations - spousteni

REM Spoustec ze webu / ze Stazenych souboru -> najdi projekt kdekoli v profilu
set "DASH="
for /f "delims=" %%i in ('powershell -NoProfile -Command "Get-ChildItem -Path $env:USERPROFILE -Filter server.py -Recurse -ErrorAction SilentlyContinue | Where-Object { Test-Path (Join-Path $_.DirectoryName '.env.example') } | Select-Object -First 1 -ExpandProperty DirectoryName"') do set "DASH=%%i"

if not defined DASH (
    echo.
    echo  [CHYBA] Projekt dashboard nebyl nalezen.
    echo  Ujistete se, ze mate slozku dashboard stazenou nekde ve svem profilu.
    echo.
    pause
    exit /b 1
)

cd /d "%DASH%"
call start-server.bat
