"""
╔══════════════════════════════════════════════════════════════════════╗
║  OmniPipe — Nuke Startup Module                                     ║
║  omnipipe/dcc/nuke/startup.py                                        ║
║                                                                      ║
║  Called once by menu.py when Nuke boots. Handles:                    ║
║    1. License validation (Layer 1 + Layer 2)                         ║
║    2. OmniPipe menu installation in Nuke's menu bar                  ║
║    3. Startup logging                                                ║
║                                                                      ║
║  If the license is invalid, Nuke opens but OmniPipe menu items       ║
║  show a warning instead of running pipeline actions.                 ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os
import sys


def _inject_omnipipe_path():
    """Ensure the OmniPipe package is importable inside Nuke's Python."""
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)
    ))))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    vendor_dir = os.path.join(repo_root, "omnipipe", "vendor")
    if os.path.isdir(vendor_dir) and vendor_dir not in sys.path:
        sys.path.insert(0, vendor_dir)


def _validate_license():
    """Returns (is_valid, message). Runs both Layer 1 and Layer 2."""
    from omnipipe.core.license import validate_license, phone_home

    valid, msg = validate_license()
    if not valid:
        return False, msg

    try:
        lic_path = os.path.join(os.path.expanduser("~"), "omnipipe.lic")
        with open(lic_path, "r") as f:
            studio_name = f.readline().strip()

        import hashlib
        studio_id = hashlib.sha256(studio_name.lower().encode()).hexdigest()[:16]
        ph_valid, ph_msg = phone_home(studio_id, studio_name, dcc="nuke")

        if not ph_valid:
            return False, ph_msg
    except Exception:
        pass

    return valid, msg


# ── Menu command callbacks ────────────────────────────────────────────────────

def _cmd_save():
    """License-gated save with feedback."""
    import nuke
    from omnipipe.dcc.nuke.api import NukeDCC

    dcc = NukeDCC()
    current = dcc.get_current_file()
    if not current:
        nuke.message("OmniPipe: Script has no name.\nUse File → Save As first.")
        return
    result = dcc.save_file()
    if result:
        nuke.message(f"OmniPipe: Saved ✓\n{os.path.basename(current)}")


def _cmd_version_up():
    """Auto version-bump and save."""
    import nuke
    from omnipipe.dcc.nuke.api import NukeDCC

    dcc = NukeDCC()
    current = dcc.get_current_file()
    if not current:
        nuke.message("OmniPipe: Script has no name.\nUse File → Save As first.")
        return
    new_path = dcc.save_version_up()
    if new_path:
        nuke.message(f"OmniPipe: Version Up ✓\n{os.path.basename(new_path)}")


def _cmd_publish():
    """Publish current script through the pipeline."""
    import nuke
    from omnipipe.dcc.nuke.api import NukeDCC

    dcc = NukeDCC()
    current = dcc.get_current_file()
    if not current:
        nuke.message("OmniPipe: No script is open.\nSave your script first.")
        return

    # Determine publish path
    if "/work/" in current:
        publish_path = current.replace("/work/", "/publish/")
    else:
        d = os.path.dirname(current)
        publish_path = os.path.join(os.path.dirname(d), "publish", os.path.basename(current))

    result = dcc.publish(publish_path)
    if result:
        nuke.message(f"OmniPipe: Published ✓\n→ {publish_path}")
    else:
        nuke.message("OmniPipe: Publish FAILED\nCheck console for details.")


def _cmd_load_latest():
    """Prompt for shot context, create Read node pointing at latest publish."""
    import nuke
    from omnipipe.dcc.nuke.api import NukeDCC

    text = nuke.getInput(
        "OmniPipe Load Latest\n\n"
        "Enter: PROJECT SEQUENCE SHOT TASK\n"
        "(space-separated)",
        "PROJ sq001 sh0010 comp"
    )

    if not text:
        return

    parts = text.strip().split()
    if len(parts) != 4:
        nuke.message("OmniPipe: Expected 4 values:\nPROJECT SEQUENCE SHOT TASK")
        return

    project, seq, shot, task = parts
    from omnipipe.core.context import PipelineContext, PathResolver

    ctx = PipelineContext(
        project=project, sequence=seq, shot=shot,
        task=task, version="001", dcc="nuke",
    )
    try:
        resolver = PathResolver()
        sample_path = resolver.resolve("publish_file_nuke", ctx)
        pub_dir = os.path.dirname(sample_path)
    except Exception as e:
        nuke.message(f"OmniPipe: Path resolution failed:\n{e}")
        return

    dcc = NukeDCC()
    success = dcc.load_latest_as_read(pub_dir)
    if not success:
        nuke.message(f"OmniPipe: No published files found in:\n{pub_dir}")


def _cmd_doctor():
    """Run omnipipe doctor check."""
    import nuke
    result = os.popen(f"{sys.executable} -m omnipipe doctor").read()
    nuke.message(f"OmniPipe Doctor Results:\n\n{result}")


def _cmd_license_blocked(msg):
    """Show license blocked message for all commands."""
    import nuke
    nuke.message(
        f"OmniPipe — License Error\n\n"
        f"{msg}\n\n"
        "Contact your Pipeline Admin to resolve."
    )


# ── Menu builder ──────────────────────────────────────────────────────────────

def _create_menu(license_valid, license_msg):
    """Create the OmniPipe menu in Nuke's menu bar."""
    import nuke

    menu_bar = nuke.menu("Nuke")
    omni_menu = menu_bar.addMenu("OmniPipe")

    if license_valid:
        omni_menu.addCommand("Save", _cmd_save, "ctrl+s")
        omni_menu.addCommand("Save Version Up", _cmd_version_up, "ctrl+shift+s")
        omni_menu.addSeparator()
        omni_menu.addCommand("Publish", _cmd_publish)
        omni_menu.addCommand("Load Latest (Read Node)", _cmd_load_latest)
        omni_menu.addSeparator()
        omni_menu.addCommand("Doctor", _cmd_doctor)
    else:
        # All menu items show licensing error
        for label in ["Save", "Save Version Up", "Publish", "Load Latest", "Doctor"]:
            omni_menu.addCommand(
                f"{label} (LOCKED)",
                lambda m=license_msg: _cmd_license_blocked(m),
            )

    print(f"[OmniPipe] Menu 'OmniPipe' installed ({'active' if license_valid else 'LOCKED'}).")


# ── Main entry point (called by menu.py) ──────────────────────────────────────

def bootstrap():
    """
    Main startup routine. Called by menu.py when Nuke boots.
    Nuke's menu.py runs after the UI is ready, so no deferral needed.
    """
    _inject_omnipipe_path()

    from omnipipe.core.logger import setup_logger
    log = setup_logger("omnipipe.nuke.startup")

    log.info("=" * 60)
    log.info("OmniPipe Nuke Startup — initializing…")
    log.info("=" * 60)

    valid, msg = _validate_license()

    if valid:
        log.info("License OK: %s", msg)
        print(f"[OmniPipe] ✅ {msg}")
    else:
        log.error("License FAILED: %s", msg)
        print(f"[OmniPipe] ❌ {msg}")

    _create_menu(valid, msg)
    log.info("OmniPipe Nuke startup complete.")
