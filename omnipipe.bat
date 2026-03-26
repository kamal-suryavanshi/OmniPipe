@echo off
REM ─────────────────────────────────────────────────────────────────────────
REM  OmniPipe — Windows Launcher  (handles both compiled binary + dev mode)
REM  Double-click or run from cmd/PowerShell:  omnipipe.bat [command] [args]
REM ─────────────────────────────────────────────────────────────────────────

SETLOCAL

SET "REPO_ROOT=%~dp0"
IF "%REPO_ROOT:~-1%"=="\" SET "REPO_ROOT=%REPO_ROOT:~0,-1%"

REM ── 1. Try the compiled Nuitka binary first (production) ──────────────────
SET "BIN_PATH=%REPO_ROOT%\bin\omnipipe-win.exe"
IF EXIST "%BIN_PATH%" (
    "%BIN_PATH%" %*
    EXIT /B %ERRORLEVEL%
)

REM ── 2. Fall back to Python dev mode ──────────────────────────────────────
SET "PYTHON="
IF EXIST "%REPO_ROOT%\venv\Scripts\python.exe"  SET "PYTHON=%REPO_ROOT%\venv\Scripts\python.exe"
IF EXIST "%REPO_ROOT%\.venv\Scripts\python.exe" SET "PYTHON=%REPO_ROOT%\.venv\Scripts\python.exe"
IF "%PYTHON%"=="" WHERE python  >NUL 2>&1 && SET "PYTHON=python"
IF "%PYTHON%"=="" WHERE python3 >NUL 2>&1 && SET "PYTHON=python3"

IF "%PYTHON%"=="" (
    echo.
    echo [ERROR] OmniPipe could not find Python 3.10+ or a compiled binary.
    echo.
    echo   To fix this, choose ONE of:
    echo     A) Run scripts\install_workstation.py to set up dependencies
    echo     B) Place the compiled omnipipe-win.exe in .\bin\
    echo.
    PAUSE
    EXIT /B 1
)

SET "PYTHONPATH=%REPO_ROOT%;%PYTHONPATH%"

REM ── 3. Show help if no args ────────────────────────────────────────────────
IF "%*"=="" (
    echo.
    echo ╔══════════════════════════════════════════════════════════════════╗
    echo ║              OmniPipe – Pipeline CLI  [Dev Mode]                ║
    echo ╚══════════════════════════════════════════════════════════════════╝
    echo.
    echo   Commands:
    echo     omnipipe context PROJECT --sequence sq001 --shot sh0010
    echo     omnipipe create-shot ROOT PROJECT sq001 sh0030
    echo     omnipipe test-dcc maya
    echo     omnipipe doctor --studio-root Z:\projects --project PROJ
    echo.
    echo   Admin scripts:
    echo     python scripts\init_studio.py --config configs\client_intake.yaml
    echo     python scripts\install_workstation.py --nas-root Z:\projects
    echo     python scripts\generate_license.py "Studio Name"
    echo     python scripts\qa_runner.py
    echo.
    "%PYTHON%" -m omnipipe --help
    PAUSE
    EXIT /B 0
)

"%PYTHON%" -m omnipipe %*
ENDLOCAL
