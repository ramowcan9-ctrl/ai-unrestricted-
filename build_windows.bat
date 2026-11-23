@echo off
setlocal
title CART3R AI - Windows EXE Builder
echo ==========================================
echo          CART3R AI - EXE BUILDER
echo ==========================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3 was not found. Install Python 3.11+ from https://www.python.org/downloads/
  echo Make sure "Add Python to PATH" is checked.
  pause
  exit /b 1
)
py -m pip install --upgrade pip pyinstaller
if errorlevel 1 goto fail
py -m PyInstaller --noconfirm --clean --onefile --windowed --name CART3R_AI cart3r_ai.py
if errorlevel 1 goto fail
echo.
echo SUCCESS! Your EXE is:
echo %CD%\dist\CART3R_AI.exe
echo.
pause
exit /b 0
:fail
echo.
echo BUILD FAILED. Review the error messages above.
pause
exit /b 1
