@echo off
chcp 65001 >nul
title Customer Portal – Travelport GOL IBE

echo.
echo  ================================
echo   Customer Portal – spousteni
echo  ================================
echo.

:: Zkontroluj Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [CHYBA] Python neni nainstalovan.
    echo Stahni z: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Zkontroluj Git
git --version >nul 2>&1
if errorlevel 1 (
    echo [UPOZORNENI] Git neni nainstalovan – automaticke aktualizace nebudou fungovat.
    echo Stahni z: https://git-scm.com/download/win
)

:: Prejdi do slozky skriptu
cd /d "%~dp0"

:: Zkontroluj .env soubor
if not exist ".env" (
    echo [INFO] Vytvarim .env ze sablony...
    copy ".env.example" ".env" >nul
    echo [INFO] Doplnte ANTHROPIC_API_KEY do souboru .env pro AI chat.
    echo.
)

:: Nainstaluj zavislosti pokud chybi
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instaluji zavislosti...
    pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo [CHYBA] Instalace zavislosti selhala.
        pause
        exit /b 1
    )
)

:: Spust kontrolu aktualizaci na pozadi (kazde 3 minuty)
start "GOL-Updater" /min cmd /c "%~dp0update_checker.bat"

echo [OK] Spoustim Customer Portal na http://localhost:8501
echo [INFO] Aktualizace ze serveru se kontroluji automaticky.
echo [INFO] Pro ukonceni zavri toto okno.
echo.

:: Spust a automaticky restartuj pri padu
:restart
:: Stahni nejnovejsi kod pred kazdym startem
git pull origin claude/new-project-setup-lle2T --quiet 2>nul && echo [INFO] Kod aktualizovan.

streamlit run app.py --server.address localhost --server.port 8501

echo.
echo [INFO] App skoncila. Restartuji za 3 sekundy... (zavri okno pro ukonceni)
timeout /t 3 /nobreak >nul
goto restart
