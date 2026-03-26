#!/usr/bin/env python3
"""
OmniPipe Wiki — Reliable Dev Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uses Python's stat() polling (no watchdog/FSEvents dependency) to detect
changes to docs/ and mkdocs.yml, then kills and restarts the MkDocs dev
server automatically.

Usage:
  python3 scripts/serve_wiki.py           # Default port 8000
  python3 scripts/serve_wiki.py --port 8080
  python3 scripts/serve_wiki.py --interval 1.5

Stop with Ctrl+C.
"""

import os
import sys
import time
import signal
import argparse
import subprocess
from pathlib import Path

REPO_ROOT  = Path(__file__).parent.parent
WATCH_DIRS = [REPO_ROOT / "docs", REPO_ROOT / "mkdocs.yml"]
POLL_INTERVAL = 2.0   # seconds between scans


def get_signatures(watch_targets: list) -> dict:
    """Return {path: mtime} for every file under the watched targets."""
    sigs = {}
    for target in watch_targets:
        t = Path(target)
        if t.is_file():
            sigs[str(t)] = t.stat().st_mtime
        elif t.is_dir():
            for p in t.rglob("*"):
                if p.is_file():
                    sigs[str(p)] = p.stat().st_mtime
    return sigs


def start_server(port: int) -> subprocess.Popen:
    print(f"\n  🚀  Starting MkDocs server on http://127.0.0.1:{port}/ …\n")
    return subprocess.Popen(
        [sys.executable, "-m", "mkdocs", "serve",
         "--dev-addr", f"127.0.0.1:{port}",
         "--no-livereload"],   # we handle restarts ourselves
        cwd=str(REPO_ROOT)
    )


def kill_server(proc: subprocess.Popen):
    if proc and proc.poll() is None:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


def main():
    parser = argparse.ArgumentParser(description="OmniPipe Wiki — Reliable Dev Server")
    parser.add_argument("--port",     type=int,   default=8000,       help="Port to serve on (default: 8000)")
    parser.add_argument("--interval", type=float, default=POLL_INTERVAL, help="Polling interval in seconds (default: 2.0)")
    args = parser.parse_args()

    print()
    print("  ╔══════════════════════════════════════════════════════════════╗")
    print("  ║        OmniPipe Wiki Server (polling-based live reload)      ║")
    print("  ╚══════════════════════════════════════════════════════════════╝")
    print(f"  Watching : docs/  +  mkdocs.yml")
    print(f"  Interval : every {args.interval}s")
    print(f"  URL      : http://127.0.0.1:{args.port}/")
    print("  Stop     : Ctrl+C")
    print()

    proc = start_server(args.port)
    last_sigs = get_signatures(WATCH_DIRS)

    try:
        while True:
            time.sleep(args.interval)

            # Check if server crashed — restart it
            if proc.poll() is not None:
                print("  ⚠️   Server stopped unexpectedly — restarting…")
                proc = start_server(args.port)
                last_sigs = get_signatures(WATCH_DIRS)
                continue

            # Poll for any changed / new / deleted files
            current_sigs = get_signatures(WATCH_DIRS)
            changes = []

            for path, mtime in current_sigs.items():
                if path not in last_sigs or last_sigs[path] != mtime:
                    changes.append(path)

            for path in last_sigs:
                if path not in current_sigs:
                    changes.append(f"[deleted] {path}")

            if changes:
                changed_display = [
                    str(Path(c).relative_to(REPO_ROOT)) if not c.startswith("[deleted]") else c
                    for c in changes
                ]
                print(f"\n  📝  Change detected: {', '.join(changed_display[:3])}"
                      + (f" (+{len(changed_display)-3} more)" if len(changed_display) > 3 else ""))
                print("  🔄  Restarting server…")
                kill_server(proc)
                time.sleep(0.5)
                proc = start_server(args.port)
                last_sigs = current_sigs

    except KeyboardInterrupt:
        print("\n\n  Shutting down wiki server… bye!\n")
        kill_server(proc)
        sys.exit(0)


if __name__ == "__main__":
    main()
