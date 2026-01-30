@echo off
echo ========================================
echo OneNote Document Processing Pipeline
echo ========================================
echo.

cd /d "%~dp0"

:: Activate virtual environment
call myenv\Scripts\activate.bat

:: Run the pipeline
python onenote\scripts\run_pipeline.py

echo.
echo ========================================
echo Pipeline finished!
echo ========================================
pause
