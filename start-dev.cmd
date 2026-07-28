@echo off
setlocal

set "PROJECT_DIR=%~dp0"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "FRONTEND_DIR=%PROJECT_DIR%frontend"
set "PROJECT_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe"
set "CODEX_PYTHON=C:\Users\张博文\Documents\Codex\2026-07-21\new-chat\backend_work\.venv\Scripts\python.exe"

if exist "%PROJECT_PYTHON%" (
    set "PYTHON_EXE=%PROJECT_PYTHON%"
) else if exist "%CODEX_PYTHON%" (
    set "PYTHON_EXE=%CODEX_PYTHON%"
) else (
    echo Backend virtual environment was not found.
    echo Run setup-dev.cmd once before starting the project.
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%\node_modules" (
    echo Frontend dependencies were not found.
    echo Run setup-dev.cmd once before starting the project.
    pause
    exit /b 1
)

start "DataMind Backend" cmd /k "cd /d ""%BACKEND_DIR%"" && ""%PYTHON_EXE%"" -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
start "DataMind Frontend" cmd /k "cd /d ""%FRONTEND_DIR%"" && npm run dev"

timeout /t 4 /nobreak >nul
start "" "http://localhost:5173"

echo DataMind development services were started.
echo Frontend: http://localhost:5173
echo API docs: http://localhost:8000/docs
endlocal
