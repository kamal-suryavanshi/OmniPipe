"""
╔══════════════════════════════════════════════════════════════════════╗
║  OmniPipe — Silhouette Startup Module                                ║
║  omnipipe/dcc/silhouette/startup.py                                   ║
║                                                                      ║
║  Called on Silhouette's startup. Handles:                            ║
║    1. License validation (Layer 1 + Layer 2)                         ║
║    2. Registration of save/publish callbacks                         ║
║    3. Startup logging                                                ║
║                                                                      ║
║  Silhouette uses fx.bind() for event callbacks and fx.menu()         ║
║  for custom menu integration.                                        ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os
import sys


def _inject_omnipipe_path():
    """Ensure the OmniPipe package is importable inside Silhouette's Python."""
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
        ph_valid, ph_msg = phone_home(studio_id, studio_name, dcc="silhouette")

        if not ph_valid:
            return False, ph_msg
    except Exception:
        pass

    return valid, msg


# ── Callback functions (registered on save/load events) ──────────────────────

def _on_save_callback():
    """Called when Silhouette saves a project. Validates license first."""
    from omnipipe.core.license import validate_license
    valid, msg = validate_license()
    if not valid:
        print(f"[OmniPipe] ❌ Save blocked: {msg}")
        return False
    print("[OmniPipe] ✅ Project saved (license OK)")
    return True


def _on_publish_callback():
    """Publish current project through the pipeline."""
    from omnipipe.dcc.silhouette.api import SilhouetteDCC

    dcc = SilhouetteDCC()
    current = dcc.get_current_file()
    if not current:
        print("[OmniPipe] ❌ No project is open. Save your project first.")
        return

    if "/work/" in current:
        publish_path = current.replace("/work/", "/publish/")
    else:
        d = os.path.dirname(current)
        publish_path = os.path.join(os.path.dirname(d), "publish", os.path.basename(current))

    result = dcc.publish(publish_path)
    if result:
        print(f"[OmniPipe] ✅ Published → {publish_path}")
    else:
        print("[OmniPipe] ❌ Publish FAILED — check console for details.")


def _on_version_up_callback():
    """Auto version-bump and save."""
    from omnipipe.dcc.silhouette.api import SilhouetteDCC

    dcc = SilhouetteDCC()
    current = dcc.get_current_file()
    if not current:
        print("[OmniPipe] ❌ No project open. Save first.")
        return

    new_path = dcc.save_version_up()
    if new_path:
        print(f"[OmniPipe] ✅ Version Up → {os.path.basename(new_path)}")


def _on_export_shapes_callback():
    """Export roto shapes to Nuke .nk format."""
    from omnipipe.dcc.silhouette.api import SilhouetteDCC

    dcc = SilhouetteDCC()
    current = dcc.get_current_file()
    if not current:
        print("[OmniPipe] ❌ No project open.")
        return

    # Default export: same dir, .nk extension
    export_path = os.path.splitext(current)[0] + "_shapes.nk"
    result = dcc.export_shapes(export_path, fmt="nuke")
    if result:
        print(f"[OmniPipe] ✅ Shapes exported → {export_path}")


# ── Menu/action registration ─────────────────────────────────────────────────

def _register_actions(license_valid, license_msg):
    """
    Register OmniPipe actions in Silhouette.

    Silhouette's fx.menu() API allows adding custom menu items.
    If not available (older versions), we register callbacks via fx.bind().
    """
    try:
        import fx

        # Try menu API first (Silhouette 2022+)
        if hasattr(fx, "menu"):
            menu = fx.menu("OmniPipe")
            if license_valid:
                menu.addAction("Save", _on_save_callback)
                menu.addAction("Save Version Up", _on_version_up_callback)
                menu.addSeparator()
                menu.addAction("Publish", _on_publish_callback)
                menu.addAction("Export Shapes (Nuke)", _on_export_shapes_callback)
            else:
                menu.addAction(f"LOCKED: {license_msg}", lambda: None)
            print(f"[OmniPipe] Menu registered ({'active' if license_valid else 'LOCKED'}).")
        else:
            # Fallback: register save callback via event binding
            if license_valid and hasattr(fx, "bind"):
                fx.bind("projectSaved", _on_save_callback)
                print("[OmniPipe] Save callback registered via fx.bind().")
            else:
                print(f"[OmniPipe] License invalid or fx.bind unavailable: {license_msg}")
    except ImportError:
        # Not running inside Silhouette
        print(f"[OmniPipe] Silhouette actions registered (dev mode): "
              f"{'active' if license_valid else 'LOCKED'}")


# ── Main entry point ─────────────────────────────────────────────────────────

def bootstrap():
    """
    Main startup routine for Silhouette.
    Called from Silhouette's startup script or manually from the console.
    """
    _inject_omnipipe_path()

    from omnipipe.core.logger import setup_logger
    log = setup_logger("omnipipe.silhouette.startup")

    log.info("=" * 60)
    log.info("OmniPipe Silhouette Startup — initializing…")
    log.info("=" * 60)

    valid, msg = _validate_license()

    if valid:
        log.info("License OK: %s", msg)
        print(f"[OmniPipe] ✅ {msg}")
    else:
        log.error("License FAILED: %s", msg)
        print(f"[OmniPipe] ❌ {msg}")

    _register_actions(valid, msg)
    log.info("OmniPipe Silhouette startup complete.")
