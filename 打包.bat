@echo off
setlocal
title Package File Interpreter

REM Change into this script's own folder (works with spaces and
REM non-ASCII characters in the path).
pushd "%~dp0"

set "TAR=%SystemRoot%\System32\tar.exe"

echo ============================================================
echo   File Interpreter - Package into a clean zip
echo ============================================================
echo.

if not exist "%TAR%" (
    echo [ERROR] tar.exe not found. Windows 10 or newer is required.
    goto :fail
)

REM Generate a timestamp so every package gets a unique name
set "STAMP="
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%I"
if not defined STAMP set "STAMP=manual"

set "ZIP_PATH=%~dp0..\file-interpreter_%STAMP%.zip"

echo [INFO] Output   : %ZIP_PATH%
echo [INFO] Excluded : .venv  node_modules  __pycache__  logs  dist  .git
echo.

"%TAR%" -a -c -f "%ZIP_PATH%" --exclude=.venv --exclude=node_modules --exclude=__pycache__ --exclude=logs --exclude=dist --exclude=.git .

if errorlevel 1 (
    echo [ERROR] Packaging failed.
    goto :fail
)

echo.
echo [OK] Package created:
echo      %ZIP_PATH%
echo.
echo Send this zip to the other person. They unzip it and
echo double-click start.bat to run.
echo.
pause
popd
exit /b 0

:fail
echo.
pause
popd
exit /b 1
