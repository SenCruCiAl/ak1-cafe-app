@echo off
cd /d "%~dp0"
python src\cafe_app.py
if errorlevel 1 pause
