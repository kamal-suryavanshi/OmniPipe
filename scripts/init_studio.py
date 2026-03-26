#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║         OmniPipe Studio Initialiser — init_studio.py               ║
║                                                                      ║
║  Run ONCE per client to bootstrap the complete folder hierarchy      ║
║  for a brand-new studio deployment.                                  ║
║                                                                      ║
║  Windows:   python scripts\init_studio.py                            ║
║  Mac/Linux: python3 scripts/init_studio.py                           ║
╚══════════════════════════════════════════════════════════════════════╝

What this script does
─────────────────────
  1. Interactively prompts for studio-specific settings (or reads a
     pre-filled config file for fully-automated CI deployments).
  2. Generates a minimal studio config (studio_settings.yaml) next to
     the existing schema.yaml.
  3. Physically creates the full folder hierarchy on disk, including
     well-known department work + publish trees, an admin area, and
     a software/vendor landing zone.
  4. Writes a .omnipipe_stamp file into the root so subsequent runs
     detect an existing installation and refuse to overwrite it
     (unless --force is passed).
  5. Prints a human-readable summary of every folder created.

IMPORTANT
─────────
  This script creates folders only — it never deletes anything.
  Run it ONCE on initial client setup. After that, new projects /
  sequences / shots should be added through the pipeline APIs or future
  `omnipipe create-shot` CLI commands.
"""

import os
import sys
import platform
import argparse
import textwrap
from datetime import datetime
from pathlib import Path

# ── stdlib-only: no omnipipe imports so this script is fully portable ──────────


STAMP_FILENAME = ".omnipipe_stamp"
SETTINGS_FILENAME = "studio_settings.yaml"

# Default department task folders created under every shot
SHOT_TASKS = [
    "anim",
    "comp",
    "fx",
    "lighting",
    "lookdev",
    "model",
    "render",
    "rig",
]

# Well-known DCC tool names — subfolders created under work/ and publish/
DCCS = ["maya", "nuke", "houdini", "blender"]

# Asset types
ASSET_TYPES = ["char", "prop", "env", "vehicle", "fx"]


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _sep():
    print("─" * 70)


def _banner():
    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║          OmniPipe Studio Initialiser  v1.0                      ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"  Platform : {platform.system()} {platform.release()}")
    print(f"  Python   : {sys.version.split()[0]}")
    print(f"  Time     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    _sep()


def _prompt(label: str, default: str) -> str:
    """Prompt the user with a sensible default value."""
    val = input(f"  {label} [{default}]: ").strip()
    return val if val else default


def _mkdir(path: Path, created: list, dry_run: bool):
    """Create directory (and parents). Record it in `created` list."""
    if not path.exists():
        if not dry_run:
            path.mkdir(parents=True, exist_ok=True)
        created.append(str(path))
    # If it already exists, silently skip — idempotent


def _write_file(path: Path, content: str, dry_run: bool):
    """Write a text file only if it doesn't already exist."""
    if not path.exists():
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────────
# Folder-tree builder
# ──────────────────────────────────────────────────────────────────────────────

def build_tree(cfg: dict, dry_run: bool) -> list:
    """
    Materialises the complete studio folder hierarchy.  Returns a list of
    all paths that were newly created (skips paths that already existed).
    """
    root      = Path(cfg["studio_root"])
    proj      = cfg["project_code"]
    sequences = cfg["sequences"]
    shots_per = cfg["shots_per_sequence"]
    created: list = []

    _sep()
    print(f"  Building folder tree under: {root}")
    print(f"  {'[DRY RUN — no folders will be created]' if dry_run else 'Mode: LIVE'}")
    _sep()

    proj_root = root / proj

    # ── 1. Top-level project directories ─────────────────────────────────────
    for top in ["sequences", "assets", "editorial", "delivery",
                "reference", "dailies", "_admin", "_archive"]:
        _mkdir(proj_root / top, created, dry_run)

    # ── 2. Asset library ──────────────────────────────────────────────────────
    for atype in ASSET_TYPES:
        for dcc in DCCS:
            for sub in ["work", "publish"]:
                _mkdir(proj_root / "assets" / atype / "_template" / sub / dcc, created, dry_run)

    # ── 3. Sequences → Shots ─────────────────────────────────────────────────
    for seq_idx in range(1, sequences + 1):
        seq_name = f"sq{seq_idx:03d}"

        for shot_idx in range(1, shots_per + 1):
            shot_name = f"sh{shot_idx:03d}0"   # e.g. sh0010, sh0020 …
            shot_root = proj_root / "sequences" / seq_name / shot_name

            # Thumbnail / editorial placeholder
            _mkdir(shot_root / "_editorial", created, dry_run)

            for task in SHOT_TASKS:
                for dcc in DCCS:
                    _mkdir(shot_root / "work"    / dcc / task, created, dry_run)
                    _mkdir(shot_root / "publish" / dcc / task, created, dry_run)

                # Render outputs (DCC-agnostic)
                _mkdir(shot_root / "render" / task, created, dry_run)
                _mkdir(shot_root / "cache"  / task, created, dry_run)

    # ── 4. Admin / Pipeline area ──────────────────────────────────────────────
    admin = proj_root / "_admin"
    for sub in ["licenses", "scripts", "configs", "docs", "logs"]:
        _mkdir(admin / sub, created, dry_run)

    # ── 5. Software / vendor landing zone ─────────────────────────────────────
    _mkdir(root / "_software", created, dry_run)
    for dcc in DCCS:
        _mkdir(root / "_software" / dcc, created, dry_run)

    # ── 6. Shared pipeline config snapshot ───────────────────────────────────
    # Copy schema.yaml into the admin/configs area as a read reference
    schema_src = Path(__file__).parent.parent / "configs" / "schema.yaml"
    if schema_src.exists() and not dry_run:
        import shutil
        dest = admin / "configs" / "schema.yaml"
        if not dest.exists():
            shutil.copy2(schema_src, dest)

    return created


# ──────────────────────────────────────────────────────────────────────────────
# Studio settings YAML writer
# ──────────────────────────────────────────────────────────────────────────────

def write_studio_settings(cfg: dict, dry_run: bool):
    """
    Writes a studio_settings.yaml alongside schema.yaml.
    This file is the single source of truth for all client-specific overrides.
    """
    content = textwrap.dedent(f"""\
        # OmniPipe Studio Settings
        # Generated by init_studio.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        # Edit this file to change studio-wide pipeline defaults.
        # DO NOT overwrite schema.yaml directly.

        studio_name:        "{cfg['studio_name']}"
        project_code:       "{cfg['project_code']}"
        studio_root:        "{cfg['studio_root']}"
        os_platform:        "{platform.system()}"
        frame_rate:         {cfg['frame_rate']}
        frame_padding:      {cfg['frame_padding']}
        color_space:        "{cfg['color_space']}"
        image_format:       "{cfg['image_format']}"

        naming_convention:
          separator: "_"
          version_padding: 3   # v001, v002 …
          forbidden_chars: [" ", "!", "@", "#", "$", "%"]
    """)

    dest = Path(__file__).parent.parent / "configs" / SETTINGS_FILENAME
    _write_file(dest, content, dry_run)
    if not dry_run:
        print(f"  [✓] Studio settings written → {dest}")
    else:
        print(f"  [DRY RUN] Would write → {dest}")


# ──────────────────────────────────────────────────────────────────────────────
# Stamp writer / checker
# ──────────────────────────────────────────────────────────────────────────────

def write_stamp(studio_root: str, project_code: str, dry_run: bool):
    path = Path(studio_root) / project_code / STAMP_FILENAME
    content = (
        f"OmniPipe Studio Install\n"
        f"Created: {datetime.now().isoformat()}\n"
        f"Platform: {platform.system()}\n"
        f"Python: {sys.version}\n"
    )
    _write_file(path, content, dry_run)


def check_existing_stamp(studio_root: str, project_code: str) -> bool:
    return (Path(studio_root) / project_code / STAMP_FILENAME).exists()


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="OmniPipe — One-time studio folder structure initialiser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              python3 scripts/init_studio.py
              python3 scripts/init_studio.py --dry-run
              python3 scripts/init_studio.py --force
        """)
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what would be created without touching the disk.")
    parser.add_argument("--force",   action="store_true",
                        help="Re-run even if a previous install stamp exists.")
    args = parser.parse_args()

    _banner()

    # ── Gather studio-specific settings interactively ─────────────────────────
    print("  Please enter details for this studio deployment.")
    print("  Press Enter to accept the default shown in [brackets].\n")

    default_root = (
        r"C:\Studio" if platform.system() == "Windows"
        else os.path.expanduser("~/Studio")
    )

    cfg = {
        "studio_name":       _prompt("Studio name",             "Acme VFX Studio"),
        "project_code":      _prompt("Project code",            "PROJ"),
        "studio_root":       _prompt("Studio root path",        default_root),
        "sequences":     int(_prompt("Number of sequences",     "5")),
        "shots_per_sequence": int(_prompt("Shots per sequence", "10")),
        "frame_rate":    int(_prompt("Frame rate (fps)",        "24")),
        "frame_padding": int(_prompt("Frame padding (digits)",  "4")),
        "color_space":       _prompt("Colour space",            "ACEScg"),
        "image_format":      _prompt("Primary image format",    "EXR"),
    }

    _sep()
    print(f"  Studio Name  : {cfg['studio_name']}")
    print(f"  Project Code : {cfg['project_code']}")
    print(f"  Studio Root  : {cfg['studio_root']}")
    print(f"  Sequences    : {cfg['sequences']}  ×  {cfg['shots_per_sequence']} shots")
    print(f"  FPS          : {cfg['frame_rate']}")
    print(f"  Colour Space : {cfg['color_space']}")
    _sep()

    # ── Guard: refuse to re-initialise without --force ─────────────────────────
    if check_existing_stamp(cfg["studio_root"], cfg["project_code"]):
        if not args.force:
            print()
            print("  ⚠  INSTALLATION ALREADY EXISTS")
            print(f"     Stamp found at: {Path(cfg['studio_root']) / cfg['project_code'] / STAMP_FILENAME}")
            print("     Run with --force to re-initialise (existing folders are kept).")
            print()
            sys.exit(0)
        else:
            print("  ⚠  --force supplied: re-running over existing installation.")

    confirm = input("  Proceed? (yes/no) [no]: ").strip().lower()
    if confirm not in ("yes", "y"):
        print("\n  Aborted. No changes were made.\n")
        sys.exit(0)

    # ── Build the tree ─────────────────────────────────────────────────────────
    created = build_tree(cfg, dry_run=args.dry_run)

    # ── Write studio_settings.yaml ─────────────────────────────────────────────
    write_studio_settings(cfg, dry_run=args.dry_run)

    # ── Stamp ──────────────────────────────────────────────────────────────────
    if not args.dry_run:
        write_stamp(cfg["studio_root"], cfg["project_code"], dry_run=False)

    # ── Summary ────────────────────────────────────────────────────────────────
    _sep()
    if args.dry_run:
        print(f"  [DRY RUN] Would have created {len(created)} folder(s).")
    else:
        print(f"  [✓] {len(created)} folder(s) created successfully.")

    print()
    if created:
        print("  Folders created (first 20 shown):")
        for p in created[:20]:
            # Display path relative to studio root for readability
            try:
                rel = Path(p).relative_to(cfg["studio_root"])
                print(f"    {rel}")
            except ValueError:
                print(f"    {p}")
        if len(created) > 20:
            print(f"    … and {len(created) - 20} more.")

    _sep()
    print(f"  OmniPipe studio initialisation {'preview' if args.dry_run else 'complete'}!")
    print(f"  Studio root : {cfg['studio_root']}/{cfg['project_code']}")
    print()


if __name__ == "__main__":
    main()
