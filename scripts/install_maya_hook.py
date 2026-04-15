#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║  OmniPipe — Maya Hook Installer                                     ║
║  scripts/install_maya_hook.py                                        ║
║                                                                      ║
║  Installs (or updates) the OmniPipe userSetup.py into Maya's        ║
║  scripts directory. Supports all platforms and Maya versions.        ║
║                                                                      ║
║  Usage:                                                              ║
║    python3 scripts/install_maya_hook.py                               ║
║    python3 scripts/install_maya_hook.py --maya-version 2025           ║
║    python3 scripts/install_maya_hook.py --maya-dir /custom/maya/dir   ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
USERSETUP_SOURCE = REPO_ROOT / "omnipipe" / "dcc" / "maya" / "userSetup.py"


def get_maya_scripts_dir(maya_version: str = None, maya_dir: str = None) -> Path:
    """Resolve the Maya scripts directory for the current platform."""
    if maya_dir:
        return Path(maya_dir)

    version = maya_version or "2025"
    home = Path.home()

    if sys.platform == "darwin":
        return home / "Library" / "Preferences" / "Autodesk" / "maya" / version / "scripts"
    elif sys.platform == "win32":
        return home / "Documents" / "maya" / version / "scripts"
    else:  # Linux
        return home / "maya" / version / "scripts"


def install_hook(scripts_dir: Path) -> bool:
    """Copy userSetup.py into Maya's scripts directory."""
    scripts_dir.mkdir(parents=True, exist_ok=True)
    target = scripts_dir / "userSetup.py"

    # Backup existing userSetup.py if it exists and wasn't ours
    if target.exists():
        content = target.read_text(encoding="utf-8")
        if "OmniPipe" in content:
            print(f"  ✅  Existing OmniPipe userSetup.py found — replacing with latest.")
        else:
            backup = target.with_suffix(".py.bak_omnipipe")
            shutil.copy2(target, backup)
            print(f"  ⚠️   Backed up existing userSetup.py → {backup.name}")
            print(f"       (Your original Maya startup code is preserved)")

    shutil.copy2(USERSETUP_SOURCE, target)
    print(f"  ✅  Installed: {target}")

    # Write OMNIPIPE_REPO_ROOT into Maya.env for this version
    maya_env_path = scripts_dir.parent / "Maya.env"
    env_line = f"OMNIPIPE_REPO_ROOT={REPO_ROOT}"

    existing_env = ""
    if maya_env_path.exists():
        existing_env = maya_env_path.read_text(encoding="utf-8")

    if "OMNIPIPE_REPO_ROOT" in existing_env:
        # Update existing line
        lines = existing_env.splitlines()
        updated = [env_line if l.startswith("OMNIPIPE_REPO_ROOT") else l for l in lines]
        maya_env_path.write_text("\n".join(updated) + "\n", encoding="utf-8")
        print(f"  ✅  Updated OMNIPIPE_REPO_ROOT in Maya.env")
    else:
        with open(maya_env_path, "a", encoding="utf-8") as f:
            f.write(f"\n# OmniPipe pipeline repo root\n{env_line}\n")
        print(f"  ✅  Added OMNIPIPE_REPO_ROOT to Maya.env")

    return True


def main():
    parser = argparse.ArgumentParser(description="Install OmniPipe userSetup.py into Maya")
    parser.add_argument("--maya-version", default="2025", help="Maya version (default: 2025)")
    parser.add_argument("--maya-dir", default=None, help="Override Maya scripts directory")
    args = parser.parse_args()

    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║     OmniPipe — Maya Hook Installer               ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print(f"  Platform:  {sys.platform}")
    print(f"  Maya ver:  {args.maya_version}")
    print()

    if not USERSETUP_SOURCE.exists():
        print(f"  ❌  Source not found: {USERSETUP_SOURCE}")
        sys.exit(1)

    scripts_dir = get_maya_scripts_dir(args.maya_version, args.maya_dir)
    print(f"  Target: {scripts_dir}")
    print()

    success = install_hook(scripts_dir)

    if success:
        print()
        print("  🎉  Maya hook installed successfully!")
        print()
        print("  Next steps:")
        print("    1. (Re)start Maya")
        print("    2. Look for the 'OmniPipe' shelf tab")
        print("    3. Check the Script Editor for startup logs")
        print()
    else:
        print("  ❌  Installation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
