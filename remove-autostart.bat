@echo off
chcp 65001 >nul
title Odinstalace automatickeho startu

set "LINK=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\AirReservationsDashboard.lnk"

echo.
echo  Odinstalovavam automaticky start Air Reservations Dashboard...
echo.

if exist "%LINK%" (
    del "%LINK%"
    echo  [OK] Automaticky start byl odstranen.
) else (
    echo  [INFO] Automaticky start nebyl nainstalovan.
)

echo.
pause
