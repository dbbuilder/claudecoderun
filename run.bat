@echo off
REM Claude Code Runner - Windows batch wrapper

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is required but not found
    echo Please install Python 3.8 or higher
    exit /b 1
)

REM Check if we should use WSL
where wsl >nul 2>&1
if %errorlevel% equ 0 (
    echo WSL is available - using Linux subsystem
    wsl bash %~dp0run.sh %*
) else (
    echo Running directly on Windows
    echo Note: This tool works best in WSL or Linux
    python "%~dp0claudecoderun.py" %*
)
