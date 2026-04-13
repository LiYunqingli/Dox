@echo off
setlocal

REM Build script for PyInstaller
REM Output: <repo_root>\main.exe

cd /d "%~dp0"

where pyinstaller >nul 2>nul
if errorlevel 1 (
    echo [ERROR] pyinstaller not found. Install it first: pip install pyinstaller
    exit /b 1
)

if exist "%CD%\main.exe" del /f /q "%CD%\main.exe"
if exist "%CD%\build" rmdir /s /q "%CD%\build"

pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --name main ^
  --distpath "%CD%" ^
  --workpath "%CD%\build" ^
  --specpath "%CD%\build" ^
  --paths "%CD%" ^
  --collect-submodules lib ^
  --collect-submodules lib.src ^
  main.py

if errorlevel 1 (
    echo [ERROR] Build failed.
    exit /b 1
)

echo [OK] Build success: "%CD%\main.exe"
exit /b 0
