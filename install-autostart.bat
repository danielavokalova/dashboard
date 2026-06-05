@echo off
chcp 65001 >nul
title Instalace automatickeho startu

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SCRIPT_DIR=%~dp0"
set "LINK=%STARTUP%\AirReservationsDashboard.lnk"

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
    echo  [OK] Hotovo. Server se bude spoustet automaticky pri prihlaseni.
    echo.
    echo  Odkaz ulozen do:
    echo  %LINK%
    echo.
    echo  Pro odinstalovani spust: remove-autostart.bat
) else (
    echo  [CHYBA] Nepodarilo se vytvorit zastupce.
)

echo.
pause
