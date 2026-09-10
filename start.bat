@echo off
setlocal
title File-Interpreter Launcher

REM ============================================================
REM  File Interpreter - one-click launcher
REM  Auto-creates .venv and node_modules when missing or broken,
REM  then starts the Flask backend and the Vite frontend.
REM ============================================================

REM Change into this script's own folder (works with spaces and
REM non-ASCII characters in the path).
pushd "%~dp0"

echo ============================================================
echo   File Interpreter - Launcher
echo ============================================================
echo.

REM ---------------- 1. Find a Python interpreter ---------------
set "PY_BASE="

py -3.13 -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PY_BASE=py -3.13"
    goto :found_python
)

py -3.12 -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PY_BASE=py -3.12"
    goto :found_python
)

py -3.11 -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PY_BASE=py -3.11"
    goto :found_python
)

py -3.10 -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PY_BASE=py -3.10"
    goto :found_python
)

python -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PY_BASE=python"
    goto :found_python
)

py -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PY_BASE=py"
    goto :found_python
)

goto :no_python

:found_python
echo [OK] Python found: %PY_BASE%
goto :ensure_venv

:no_python
echo [ERROR] Python 3 was not found on this computer.
echo.
echo   Please install Python 3.13 from:
echo     https://www.python.org/downloads/
echo   and tick "Add python.exe to PATH" during setup.
echo.
goto :fatal

REM ---------------- 2. Ensure the virtual env exists ------------
:ensure_venv
if not exist ".venv\Scripts\python.exe" goto :make_venv
".venv\Scripts\python.exe" -c "import sys" >nul 2>&1
if errorlevel 1 goto :make_venv
echo [OK] Virtual environment .venv ready.
goto :ensure_deps

:make_venv
echo [INFO] .venv is missing or broken, creating a fresh one ...
if exist ".venv" rmdir /s /q ".venv"
%PY_BASE% -m venv .venv
if errorlevel 1 (
    echo [ERROR] Could not create the virtual environment.
    goto :fatal
)
echo [OK] Virtual environment created.
goto :ensure_deps

REM ---------------- 3. Install Python dependencies --------------
:ensure_deps
".venv\Scripts\python.exe" -c "import flask, flask_cors, magika" >nul 2>&1
if not errorlevel 1 goto :deps_ok
echo [INFO] Installing Python dependencies from requirements.txt ...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] pip install failed.
    echo   - Check your internet connection.
    echo   - magika needs Python 3.13, 3.14 may not have wheels yet.
    goto :fatal
)
:deps_ok
echo [OK] Python dependencies ready.
goto :ensure_frontend

REM ---------------- 4. Ensure frontend dependencies -------------
:ensure_frontend
set "NPM_OK=1"
where npm >nul 2>&1
if errorlevel 1 (
    set "NPM_OK=0"
    goto :frontend_done
)

if exist "node_modules\.bin\vite.cmd" goto :frontend_done
if exist "node_modules\.bin\vite" goto :frontend_done

echo [INFO] Installing frontend dependencies with npm install ...
call npm install
if errorlevel 1 (
    echo [WARN] npm install failed. Backend still runs, frontend skipped.
    set "NPM_OK=0"
    goto :frontend_done
)

:frontend_done
if "%NPM_OK%"=="0" (
    echo [WARN] Node.js / npm not available, frontend will be skipped.
) else (
    echo [OK] Frontend dependencies ready.
)

REM ---------------- 5. Start backend and frontend ---------------
echo.
echo [1/2] Starting backend  Flask   http://127.0.0.1:5000 ...
start "Backend - Flask :5000" /D "%~dp0" cmd /k ".venv\Scripts\python.exe server.py"

if "%NPM_OK%"=="1" (
    echo [2/2] Starting frontend Vite   http://localhost:5173 ...
    start "Frontend - Vite :5173" /D "%~dp0" cmd /k "npm run dev"
) else (
    echo [2/2] Frontend skipped - npm not available.
)

echo.
echo ============================================================
echo   Services are starting in separate windows:
echo     Backend  : http://127.0.0.1:5000
echo     Frontend : http://localhost:5173
echo   Close a window to stop that service.
echo ============================================================
echo.

if "%NPM_OK%"=="1" (
    echo Opening the browser in 3 seconds ...
    timeout /t 3 /nobreak >nul
    start "" "http://localhost:5173"
) else (
    echo Frontend was skipped, so no browser will open.
    echo The backend API is running at http://127.0.0.1:5000
)

popd
exit /b 0

:fatal
echo.
echo Setup could not be completed. Please read the messages above.
echo Tip: delete the ".venv" and "node_modules" folders, then run this again.
echo.
pause
popd
exit /b 1
