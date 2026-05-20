@echo off
chcp 65001 >nul
title Instalace automatického startu

set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SCRIPT_DIR=%~dp0
set LINK=%STARTUP%\AirReservationsDashboard.lnk

echo.
echo  Instaluji Air Reservations Dashboard do Startupu Windows...
echo.

powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; ^
   $s = $ws.CreateShortcut('%LINK%'); ^
   $s.TargetPath = '%SCRIPT_DIR%start-server.bat'; ^
   $s.WorkingDirectory = '%SCRIPT_DIR%'; ^
   $s.WindowStyle = 7; ^
   $s.Description = 'Air Reservations Dashboard'; ^
   $s.Save()"

if exist "%LINK%" (
    echo  [OK]  Hotovo! Server se bude spouštět automaticky při přihlášení.
    echo.
    echo  Odkaz uložen do:
    echo  %LINK%
    echo.
    echo  Pro odinstalování spusť: remove-autostart.bat
) else (
    echo  [CHYBA] Nepodařilo se vytvořit zástupce.
)

echo.
pause
