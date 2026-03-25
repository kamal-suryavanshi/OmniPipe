@echo off
:: OmniPipe Windows Smart Launcher
set BIN_PATH="%~dp0bin\omnipipe-win.exe"

if exist %BIN_PATH% (
    :: Execute the secure Nuitka binary directly
    %BIN_PATH% %*
) else (
    echo Compiled Nuitka binary not found for Windows! (%BIN_PATH%)
    echo As a developer, please run 'python build.py' on this Windows machine first to compile the C++ binary.
    pause
)
