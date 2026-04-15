#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║  OmniPipe — Nuke Hook Installer                                     ║
║  scripts/install_nuke_hook.py                                        ║
║                                                                      ║
║  Installs (or updates) the OmniPipe menu.py into Nuke's plugin      ║
║  directory. Supports all platforms and Nuke versions.                 ║
║                                                                      ║
║  Usage:                                                              ║
║    python3 scripts/install_nuke_hook.py                               ║
║    python3 scripts/install_nuke_hook.py --nuke-version 15.1          ║
║    python3 scripts/install_nuke_hook.py --nuke-dir /custom/nuke/dir  ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MENU_SOURCE = REPO_ROOT / "omnipipe" / "dcc" / "nuke" / "menu.py"


def get_nuke_plugin_dir(nuke_version: str = None, nuke_dir: str = None) -> Path:
    """Resolve the Nuke plugin directory for the current platform."""
    if nuke_dir:
        return Path(nuke_dir)

    version = nuke_version or "15.1"
    home = Path.home()

    if sys.platform == "darwin":
        return home / ".nuke"
    elif sys.platform == "win32":
        return home / ".nuke"
    else:  # Linux
        return home / ".nuke"


def install_hook(plugin_dir: Path) -> bool:
    """Copy menu.py into Nuke's plugin directory."""
    plugin_dir.mkdir(parents=True, exist_ok=True)
    target = plugin_dir / "menu.py"

    # Backup existing menu.py if it exists and wasn't ours
    if target.exists():
        content = target.read_text(encoding="utf-8")
        if "OmniPipe" in content:
            print(f"  ✅  Existing OmniPipe menu.py found — replacing with latest.")
        else:
            backup = target.with_suffix(".py.bak_omnipipe")
            shutil.copy2(target, backup)
            print(f"  ⚠️   Backed up existing menu.py → {backup.name}")
            print(f"       (Your original Nuke menu code is preserved)")

    shutil.copy2(MENU_SOURCE, target)
    print(f"  ✅  Installed: {target}")

    # Set OMNIPIPE_REPO_ROOT in init.py (Nuke's startup env file)
    init_path = plugin_dir / "init.py"
    env_line = f'import os; os.environ["OMNIPIPE_REPO_ROOT"] = r"{REPO_ROOT}"'

    existing = ""
    if init_path.exists():
        existing = init_path.read_text(encoding="utf-8")

    if "OMNIPIPE_REPO_ROOT" in existing:
        lines = existing.splitlines()
        updated = [env_line if "OMNIPIPE_REPO_ROOT" in l else l for l in lines]
        init_path.write_text("\n".join(updated) + "\n", encoding="utf-8")
        print(f"  ✅  Updated OMNIPIPE_REPO_ROOT in init.py")
    else:
        with open(init_path, "a", encoding="utf-8") as f:
            f.write(f"\n# OmniPipe pipeline repo root\n{env_line}\n")
        print(f"  ✅  Added OMNIPIPE_REPO_ROOT to init.py")

    return True


def main():
    parser = argparse.ArgumentParser(description="Install OmniPipe menu.py into Nuke")
    parser.add_argument("--nuke-version", default="15.1", help="Nuke version (default: 15.1)")
    parser.add_argument("--nuke-dir", default=None, help="Override Nuke plugin directory")
    args = parser.parse_args()

    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║     OmniPipe — Nuke Hook Installer               ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print(f"  Platform:  {sys.platform}")
    print(f"  Nuke ver:  {args.nuke_version}")
    print()

    if not MENU_SOURCE.exists():
        print(f"  ❌  Source not found: {MENU_SOURCE}")
        sys.exit(1)

    plugin_dir = get_nuke_plugin_dir(args.nuke_version, args.nuke_dir)
    print(f"  Target: {plugin_dir}")
    print()

    success = install_hook(plugin_dir)

    if success:
        print()
        print("  🎉  Nuke hook installed successfully!")
        print()
        print("  Next steps:")
        print("    1. (Re)start Nuke")
        print("    2. Look for the 'OmniPipe' menu in the menu bar")
        print("    3. Check the Script Editor for startup logs")
        print()
    else:
        print("  ❌  Installation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
