@echo off
echo Starting New Help Portal...
cd /d "%~dp0"

:: Install dependencies if needed
pip install -r requirements.txt -q

:: Start Streamlit and open browser
start "" http://localhost:8501
streamlit run app.py --server.headless false
