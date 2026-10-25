@echo off
REM Voice Slideshow Maker - Windows startup script

echo ========================================
echo Voice Slideshow Maker
echo ========================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

echo.
echo Starting application...
echo Open your browser to: http://localhost:5000
echo.

python app.py

pause
