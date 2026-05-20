@echo off
chcp 65001 >nul
title Odinstalace automatického startu

set LINK=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\AirReservationsDashboard.lnk

if exist "%LINK%" (
    del "%LINK%"
    echo  [OK]  Server se již nebude spouštět automaticky.
) else (
    echo  [INFO] Zástupce nebyl nalezen – nic k odinstalování.
)

echo.
pause
