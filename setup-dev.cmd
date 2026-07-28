@echo off
setlocal

set "PROJECT_DIR=%~dp0"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "FRONTEND_DIR=%PROJECT_DIR%frontend"

echo [1/2] Preparing backend...
if not exist "%BACKEND_DIR%\.venv\Scripts\python.exe" (
    python -m venv "%BACKEND_DIR%\.venv"
    if errorlevel 1 goto :failed
)
"%BACKEND_DIR%\.venv\Scripts\python.exe" -m pip install -e "%BACKEND_DIR%[dev]"
if errorlevel 1 goto :failed

echo [2/2] Preparing frontend...
pushd "%FRONTEND_DIR%"
call npm install
if errorlevel 1 (
    popd
    goto :failed
)
popd

echo Setup completed. Double-click start-dev.cmd to run the project.
pause
exit /b 0

:failed
echo Setup failed. Check Python, Node.js, npm, and the network connection.
pause
exit /b 1
