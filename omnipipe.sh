#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
#  OmniPipe — Mac / Linux Launcher
#  Make executable once: chmod +x omnipipe.sh
#  Then run: ./omnipipe.sh [command] [args]
#    OR add an alias: alias omnipipe="$(pwd)/omnipipe.sh"
# ─────────────────────────────────────────────────────────────────────────────

set -e

# Resolve the repo root robustly (works with symlinks)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &>/dev/null && pwd )"
REPO_ROOT="$SCRIPT_DIR"

# Detect OS for the compiled binary name
OS="$(uname)"
case "$OS" in
  'Darwin') BIN_NAME="omnipipe-mac" ;;
  'Linux')  BIN_NAME="omnipipe-linux" ;;
  *)        BIN_NAME="" ;;
esac

# ── 1. Try compiled Nuitka binary first (production) ─────────────────────────
BIN_PATH="$REPO_ROOT/bin/$BIN_NAME"
if [ -n "$BIN_NAME" ] && [ -f "$BIN_PATH" ]; then
    exec "$BIN_PATH" "$@"
fi

# ── 2. Fall back to Python dev mode ──────────────────────────────────────────
PYTHON=""
if   [ -f "$REPO_ROOT/venv/bin/python"  ];  then PYTHON="$REPO_ROOT/venv/bin/python"
elif [ -f "$REPO_ROOT/.venv/bin/python" ];  then PYTHON="$REPO_ROOT/.venv/bin/python"
elif command -v python3 &>/dev/null;        then PYTHON="python3"
elif command -v python  &>/dev/null;        then PYTHON="python"
fi

if [ -z "$PYTHON" ]; then
    echo ""
    echo "  [ERROR] OmniPipe could not find Python 3.10+ or a compiled binary."
    echo ""
    echo "  To fix this, choose ONE of:"
    echo "    A) Run: python3 scripts/install_workstation.py"
    echo "    B) Build and place the compiled binary in ./bin/$BIN_NAME"
    echo ""
    exit 1
fi

export PYTHONPATH="$REPO_ROOT:$PYTHONPATH"

# ── 3. Show help when run with no arguments ───────────────────────────────────
if [ $# -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║              OmniPipe – Pipeline CLI  [Dev Mode]                ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "  Commands:"
    echo "    ./omnipipe.sh context PROJECT --sequence sq001 --shot sh0010"
    echo "    ./omnipipe.sh create-shot /mnt/nas PROJECT sq001 sh0030"
    echo "    ./omnipipe.sh test-dcc maya"
    echo "    ./omnipipe.sh doctor --studio-root /mnt/nas --project PROJ"
    echo ""
    echo "  Admin scripts:"
    echo "    python3 scripts/init_studio.py --config configs/client_intake.yaml"
    echo "    python3 scripts/install_workstation.py --nas-root /mnt/nas/projects"
    echo "    python3 scripts/generate_license.py 'Studio Name'"
    echo "    python3 scripts/qa_runner.py"
    echo ""
    "$PYTHON" -m omnipipe --help
    exit 0
fi

exec "$PYTHON" -m omnipipe "$@"
