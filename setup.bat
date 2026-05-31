@echo off
cd /d "%~dp0"
echo Creating virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat
pip install ttkbootstrap
echo.
echo Done. Run with: run.bat
pause
