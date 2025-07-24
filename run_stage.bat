@echo off
REM Claude Code Runner with Stage Support - Windows batch wrapper

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is required but not found
    echo Please install Python 3.8 or higher
    exit /b 1
)

REM Check for --list-stages flag
echo %* | findstr /C:"--list-stages" >nul
if %errorlevel% equ 0 (
    python "%~dp0claudecoderun_stage.py" --list-stages
    exit /b 0
)

REM Check for --stage flag
echo %* | findstr /C:"--stage" >nul
if %errorlevel% equ 0 (
    echo Using stage-aware version
    set SCRIPT=claudecoderun_stage.py
    goto :run
)

REM Check if we should use WSL
where wsl >nul 2>&1
if %errorlevel% equ 0 (
    echo WSL is available - using Linux subsystem
    wsl bash %~dp0run_stage.sh %*
) else (
    echo Running directly on Windows
    echo Note: This tool works best in WSL or Linux
    set SCRIPT=claudecoderun.py
    goto :run
)
exit /b 0

:run
python "%~dp0%SCRIPT%" %*