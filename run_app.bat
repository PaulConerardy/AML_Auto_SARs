@echo off
echo ==========================================
echo       AML SAR Assistant Launcher
echo ==========================================

echo [1/3] Checking environment...
if not exist ".env" (
    echo Creating .env from .env.example...
    copy ".env.example" ".env"
) else (
    echo .env already exists.
)

echo [2/3] Running Data Ingestion...
python src/ingestion/indexer.py
if %ERRORLEVEL% NEQ 0 (
    echo Ingestion failed! Please check if dependencies are installed or run: pip install -r requirements.txt
    pause
    exit /b %ERRORLEVEL%
)

echo [3/3] Starting User Interface...
streamlit run src/ui/app.py

pause
