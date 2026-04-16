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

:: Prejdi do slozky skriptu
cd /d "%~dp0"

:: Zkontroluj .env soubor
if not exist ".env" (
    echo [UPOZORNENI] Soubor .env nenalezen – kopiruji z .env.example
    copy ".env.example" ".env" >nul
    echo Otevri soubor .env a doplň svuj ANTHROPIC_API_KEY pro AI chat.
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

echo [OK] Spoustim Customer Portal na http://localhost:8501
echo [INFO] Pro ukonceni stiskni Ctrl+C v tomto okne
echo.

:: Spust Streamlit
:restart
streamlit run app.py --server.address localhost --server.port 8501
echo.
echo [INFO] App skoncila. Restartuji za 3 sekundy... (Ctrl+C pro ukonceni)
timeout /t 3 /nobreak >nul
goto restart
