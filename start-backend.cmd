@echo off
setlocal

set "PROJECT_DIR=%~dp0"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "PYTHON_EXE=%BACKEND_DIR%\.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Backend virtual environment was not found:
    echo %PYTHON_EXE%
    echo Run setup-dev.cmd first.
    pause
    exit /b 1
)

cd /d "%BACKEND_DIR%"
echo Starting DataMind backend...
echo API:     http://127.0.0.1:8000
echo Swagger: http://127.0.0.1:8000/docs
echo Health:  http://127.0.0.1:8000/health
echo Press Ctrl+C to stop.

"%PYTHON_EXE%" -B -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

endlocal
