#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║     OmniPipe Artist Workstation Installer — install_workstation.py  ║
║                                                                      ║
║  Run ONCE on each new artist machine to fully configure it for the  ║
║  OmniPipe pipeline.                                                  ║
║                                                                      ║
║  Windows:   python scripts\install_workstation.py                    ║
║  Mac/Linux: python3 scripts/install_workstation.py                   ║
╚══════════════════════════════════════════════════════════════════════╝

What this script does
─────────────────────
  1. Verifies Python version and critical pip dependencies.
  2. Installs any missing dependencies from requirements.txt.
  3. Optionally copies omnipipe.lic from the NAS _admin/licenses folder.
  4. Validates the installed license is valid and not tampered.
  5. Writes a per-machine .omnipipe_workstation file so the TD can
     verify which machines are configured.
  6. Runs a smoke test (context resolution + DCC dev-mode hooks).
  7. Prints a final PASS / FAIL summary.
"""

import os
import sys
import subprocess
import platform
import shutil
from datetime import datetime
from pathlib import Path

# ── stdlib only — no omnipipe imports before deps are confirmed ─────────────

MIN_PYTHON  = (3, 10)
STAMP_FILE  = Path.home() / ".omnipipe_workstation"
LIC_FILE    = Path.home() / "omnipipe.lic"
REPO_ROOT   = Path(__file__).parent.parent


def _sep(): print("─" * 70)
def _ok(msg):   print(f"  ✅  {msg}")
def _warn(msg): print(f"  ⚠️   {msg}")
def _fail(msg): print(f"  ❌  {msg}")
def _info(msg): print(f"  →   {msg}")


def check_python() -> bool:
    v = sys.version_info
    if v >= MIN_PYTHON:
        _ok(f"Python {v.major}.{v.minor}.{v.micro} — meets minimum {MIN_PYTHON[0]}.{MIN_PYTHON[1]}")
        return True
    _fail(f"Python {v.major}.{v.minor} is BELOW minimum required {MIN_PYTHON[0]}.{MIN_PYTHON[1]}")
    return False


def install_dependencies() -> bool:
    req_file = REPO_ROOT / "requirements.txt"
    if not req_file.exists():
        _warn("requirements.txt not found — skipping pip install.")
        return True

    _info("Installing / verifying pip dependencies…")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(req_file), "--quiet"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        _ok("All pip dependencies satisfied.")
        return True
    _fail(f"pip install failed:\n{result.stderr}")
    return False


def copy_license(nas_root: str = None) -> bool:
    """Optionally copies the license from the NAS admin folder."""
    if LIC_FILE.exists():
        _ok(f"License already present at {LIC_FILE}")
        return True

    if not nas_root:
        _warn("No NAS root provided — skipping license copy. "
              "Place omnipipe.lic manually at ~/omnipipe.lic")
        return False

    # Search _admin/licenses/ under any project folder on the NAS
    for project_dir in Path(nas_root).iterdir():
        candidate = project_dir / "_admin" / "licenses" / "omnipipe.lic"
        if candidate.exists():
            shutil.copy2(candidate, LIC_FILE)
            _ok(f"License copied from {candidate} → {LIC_FILE}")
            return True

    _warn(f"omnipipe.lic not found under {nas_root}/*/_admin/licenses/")
    return False


def validate_license() -> bool:
    """Cryptographically validates the installed license."""
    if not LIC_FILE.exists():
        _fail("No license file found — save/publish will be blocked.")
        return False
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from omnipipe.core.license import validate_license as _vl
        ok, msg = _vl()
        if ok:
            _ok(f"License valid — {msg}")
            return True
        _fail(f"License INVALID: {msg}")
        return False
    except Exception as e:
        _warn(f"Could not validate license (pipeline not importable yet?): {e}")
        return False


def run_smoke_test() -> bool:
    """Quick sanity check: resolve a context path and ping both DCC hooks."""
    _info("Running smoke tests…")
    passed = True

    # Context resolution
    result = subprocess.run(
        [sys.executable, "-m", "omnipipe", "context", "SMOKE_TEST",
         "--sequence", "sq001", "--shot", "sh0010"],
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    if result.returncode == 0:
        _ok("Context resolution smoke test PASSED")
    else:
        _fail(f"Context resolution FAILED:\n{result.stderr.strip()}")
        passed = False

    # DCC hooks
    for dcc in ["maya", "nuke"]:
        r = subprocess.run(
            [sys.executable, "-m", "omnipipe", "test-dcc", dcc],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        if r.returncode == 0:
            _ok(f"{dcc.upper()} DCC hook smoke test PASSED")
        else:
            _warn(f"{dcc.upper()} DCC test returned non-zero (may be expected in headless env)")

    return passed


def write_workstation_stamp():
    content = (
        f"OmniPipe Workstation Install\n"
        f"Date     : {datetime.now().isoformat()}\n"
        f"Hostname : {platform.node()}\n"
        f"Platform : {platform.system()} {platform.release()}\n"
        f"Python   : {sys.version}\n"
        f"User     : {os.getenv('USER', os.getenv('USERNAME', 'unknown'))}\n"
    )
    STAMP_FILE.write_text(content, encoding="utf-8")
    _ok(f"Workstation stamp written: {STAMP_FILE}")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="OmniPipe Artist Workstation Installer"
    )
    parser.add_argument("--nas-root", metavar="PATH",
                        help="NAS studio root path to auto-copy license from "
                             "(e.g. /mnt/nas/projects or Z:\\projects)")
    parser.add_argument("--skip-deps", action="store_true",
                        help="Skip pip dependency installation.")
    parser.add_argument("--skip-smoke", action="store_true",
                        help="Skip smoke tests.")
    args = parser.parse_args()

    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║       OmniPipe Artist Workstation Setup                         ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"  Machine  : {platform.node()}")
    print(f"  Platform : {platform.system()} {platform.release()}")
    print(f"  User     : {os.getenv('USER', os.getenv('USERNAME', 'unknown'))}")
    _sep()

    results = {}

    # 1 — Python version
    results["python"]  = check_python()

    # 2 — Dependencies
    if not args.skip_deps:
        results["deps"]    = install_dependencies()
    else:
        _info("Skipping pip install (--skip-deps)")
        results["deps"]    = True

    # 3 — License
    results["license"] = copy_license(args.nas_root)
    results["lic_ok"]  = validate_license()

    # 4 — Smoke test
    if not args.skip_smoke:
        results["smoke"]   = run_smoke_test()
    else:
        _info("Skipping smoke tests (--skip-smoke)")
        results["smoke"]   = True

    # 5 — Stamp
    write_workstation_stamp()

    _sep()
    passed = all(results.values())
    if passed:
        print("\n  🎉  Workstation setup COMPLETE — this machine is pipeline-ready!\n")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"\n  ⚠️   Setup completed with warnings: {', '.join(failed)}")
        print("       Review the items above and re-run if needed.\n")

    _sep()


if __name__ == "__main__":
    main()
