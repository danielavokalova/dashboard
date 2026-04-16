@echo off
:: Bezí na pozadí – kazde 3 minuty zkontroluje nové commity.
:: Pokud jsou zmeny, stahne je a restartuje Streamlit.

:loop
timeout /t 180 /nobreak >nul

cd /d "%~dp0"

:: Porovnej lokalni a remote HEAD
git fetch origin claude/new-project-setup-lle2T --quiet 2>nul

for /f %%i in ('git rev-parse HEAD 2^>nul') do set LOCAL=%%i
for /f %%i in ('git rev-parse origin/claude/new-project-setup-lle2T 2^>nul') do set REMOTE=%%i

if "%LOCAL%" neq "%REMOTE%" (
    echo [%time%] Nalezena nova verze – stahuji aktualizaci...
    git pull origin claude/new-project-setup-lle2T --quiet 2>nul

    :: Nainstaluj nove zavislosti pokud se zmenily
    pip install -r requirements.txt --quiet 2>nul

    :: Restartuj Streamlit (ukonci starý proces, start.bat ho spusti znovu)
    taskkill /f /im streamlit.exe >nul 2>&1
    taskkill /f /fi "WINDOWTITLE eq Customer Portal*" >nul 2>&1
    echo [%time%] Aktualizace dokoncena. App se restartuje.
)

goto loop
