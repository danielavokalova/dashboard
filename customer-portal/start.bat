@echo off
echo Starting New Help Portal...
cd /d "%~dp0"

:: Find a free port starting from 8501
set PORT=8501
:checkport
netstat -an | find ":%PORT% " >nul 2>&1
if not errorlevel 1 (
    set /a PORT+=1
    goto checkport
)

:: Install dependencies if needed
pip install -r requirements.txt -q

:: Open browser after 3 seconds and start app
start "" timeout /t 3 >nul & start "" "http://localhost:%PORT%"
streamlit run app.py --server.port %PORT% --server.headless false
