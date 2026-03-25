#!/bin/bash
# OmniPipe Mac/Linux Smart Launcher

OS="`uname`"
case $OS in
  'Linux')
    OS='linux'
    ;;
  'Darwin') 
    OS='mac'
    ;;
  *) ;;
esac

# Resolve absolute path to script folder safely
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BIN_PATH="$SCRIPT_DIR/bin/omnipipe-${OS}"

if [ -f "$BIN_PATH" ]; then
    # Execute the secure Nuitka binary directly
    "$BIN_PATH" "$@"
else
    echo "Compiled Nuitka binary not found for your OS! ($BIN_PATH)"
    echo "As a developer, please run 'python build.py' on this machine first to compile the C++ binary."
    exit 1
fi
