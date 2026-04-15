"""
╔══════════════════════════════════════════════════════════════════════╗
║  OmniPipe — Maya Startup Module                                     ║
║  omnipipe/dcc/maya/startup.py                                        ║
║                                                                      ║
║  Called once by userSetup.py when Maya boots. Handles:               ║
║    1. License validation (Layer 1 — local .lic)                      ║
║    2. License phone-home (Layer 2 — server heartbeat)                ║
║    3. OmniPipe shelf installation (Save / Publish / Load Latest)     ║
║    4. Startup logging                                                ║
║                                                                      ║
║  If the license is invalid, Maya opens but all OmniPipe shelf       ║
║  buttons are disabled with a warning dialog.                         ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os
import sys


def _inject_omnipipe_path():
    """Ensure the OmniPipe package is importable inside Maya's Python."""
    # Walk up from this file to find the repo root
    # this file: {repo}/omnipipe/dcc/maya/startup.py → 3 parents up
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)
    ))))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    # Also inject vendor dir for zero-install deps
    vendor_dir = os.path.join(repo_root, "omnipipe", "vendor")
    if os.path.isdir(vendor_dir) and vendor_dir not in sys.path:
        sys.path.insert(0, vendor_dir)


def _validate_license():
    """Returns (is_valid, message). Runs both Layer 1 and Layer 2."""
    from omnipipe.core.license import validate_license, phone_home

    # Layer 1: local .lic check
    valid, msg = validate_license()
    if not valid:
        return False, msg

    # Layer 2: phone-home heartbeat (non-blocking — uses grace period)
    try:
        # Read studio info from the .lic payload
        lic_path = os.path.join(os.path.expanduser("~"), "omnipipe.lic")
        with open(lic_path, "r") as f:
            studio_name = f.readline().strip()

        import hashlib
        studio_id = hashlib.sha256(studio_name.lower().encode()).hexdigest()[:16]
        ph_valid, ph_msg = phone_home(studio_id, studio_name, dcc="maya")

        if not ph_valid:
            return False, ph_msg
    except Exception as e:
        # Don't block Maya launch if phone-home has an unexpected error
        pass

    return valid, msg


def _create_shelf():
    """
    Creates (or refreshes) the 'OmniPipe' shelf tab in Maya with buttons
    for the core pipeline actions.
    """
    import maya.cmds as cmds
    import maya.mel as mel

    shelf_name = "OmniPipe"

    # Delete existing shelf if present (avoids duplicates on reload)
    if cmds.shelfLayout(shelf_name, exists=True):
        cmds.deleteUI(shelf_name)

    # Get the top-level shelf widget
    top_shelf = mel.eval('$tmpVar=$gShelfTopLevel')
    cmds.shelfLayout(shelf_name, parent=top_shelf)

    # ── Save button ───────────────────────────────────────────────────────
    cmds.shelfButton(
        parent=shelf_name,
        label="OP Save",
        annotation="OmniPipe: Save current scene (license-gated)",
        image1="save.png",
        command=_shelf_cmd_save(),
        sourceType="python",
    )

    # ── Version Up button ─────────────────────────────────────────────────
    cmds.shelfButton(
        parent=shelf_name,
        label="OP Save +1",
        annotation="OmniPipe: Auto version-bump and save (_v003 → _v004)",
        image1="saveAs.png",
        command=_shelf_cmd_version_up(),
        sourceType="python",
    )

    # ── Publish button ────────────────────────────────────────────────────
    cmds.shelfButton(
        parent=shelf_name,
        label="OP Publish",
        annotation="OmniPipe: Publish current scene through the pipeline",
        image1="publish.png",
        command=_shelf_cmd_publish(),
        sourceType="python",
    )

    # ── Load Latest button ────────────────────────────────────────────────
    cmds.shelfButton(
        parent=shelf_name,
        label="OP Load",
        annotation="OmniPipe: Load the latest published version",
        image1="reference.png",
        command=_shelf_cmd_load_latest(),
        sourceType="python",
    )

    # ── Doctor button ─────────────────────────────────────────────────────
    cmds.shelfButton(
        parent=shelf_name,
        label="OP Doctor",
        annotation="OmniPipe: Run environment health check",
        image1="info.png",
        command=_shelf_cmd_doctor(),
        sourceType="python",
    )

    print("[OmniPipe] Shelf 'OmniPipe' installed with 5 buttons.")


def _shelf_cmd_save():
    return """
import maya.cmds as cmds
from omnipipe.dcc.maya.api import MayaDCC

dcc = MayaDCC()
current = dcc.get_current_file()
if not current:
    cmds.warning('OmniPipe: Scene has no name. Use File → Save As first, or OP Save +1.')
else:
    result = dcc.save_file()
    if result:
        cmds.inViewMessage(msg='<span style="color:#00ff88;">OmniPipe: Saved ✓</span>', pos='topCenter', fade=True)
    else:
        cmds.warning('OmniPipe: Save FAILED — check Script Editor for details.')
"""


def _shelf_cmd_version_up():
    return """
import maya.cmds as cmds
from omnipipe.dcc.maya.api import MayaDCC
import os

dcc = MayaDCC()
current = dcc.get_current_file()
if not current:
    cmds.warning('OmniPipe: Scene has no name. Use File → Save As first.')
else:
    new_path = dcc.save_version_up()
    if new_path:
        name = os.path.basename(new_path)
        cmds.inViewMessage(msg=f'<span style="color:#00ff88;">Version Up: {name} ✓</span>', pos='topCenter', fade=True)
    else:
        cmds.warning('OmniPipe: Version Up FAILED — check Script Editor.')
"""


def _shelf_cmd_publish():
    return """
import maya.cmds as cmds, os
from omnipipe.dcc.maya.api import MayaDCC

dcc = MayaDCC()
current = dcc.get_current_file()
if not current:
    cmds.warning('OmniPipe: No scene is open. Save your scene first.')
else:
    # Determine publish path: swap /work/ → /publish/ in the file path
    if '/work/' in current:
        publish_path = current.replace('/work/', '/publish/')
    else:
        # Fallback: put in a 'publish' sibling directory
        d = os.path.dirname(current)
        publish_path = os.path.join(os.path.dirname(d), 'publish', os.path.basename(current))
    result = dcc.publish(publish_path)
    if result:
        cmds.inViewMessage(msg='<span style="color:#00ff88;">OmniPipe: Published ✓</span>', pos='topCenter', fade=True)
    else:
        cmds.warning('OmniPipe: Publish FAILED — check Script Editor for details.')
"""


def _shelf_cmd_load_latest():
    return """
import maya.cmds as cmds

# Prompt the artist for shot context
result = cmds.promptDialog(
    title='OmniPipe Load Latest',
    message='Enter: PROJECT SEQUENCE SHOT TASK (space-separated)',
    button=['Load', 'Cancel'],
    defaultButton='Load',
    cancelButton='Cancel',
    dismissString='Cancel'
)

if result == 'Load':
    import os, sys
    text = cmds.promptDialog(query=True, text=True)
    parts = text.strip().split()
    if len(parts) != 4:
        cmds.warning('OmniPipe: Expected 4 values: PROJECT SEQUENCE SHOT TASK')
    else:
        project, seq, shot, task = parts
        from omnipipe.core.context import PipelineContext, PathResolver
        from omnipipe.core.versioning import get_latest_version, parse_version
        ctx = PipelineContext(project=project, sequence=seq, shot=shot, task=task, version='001', dcc='maya')
        resolver = PathResolver()
        try:
            sample_path = resolver.resolve('publish_file_maya', ctx)
            pub_dir = os.path.dirname(sample_path)
            if not os.path.isdir(pub_dir):
                cmds.warning(f'OmniPipe: No publish directory found at {pub_dir}')
            else:
                best_file, best_ver = None, 0
                for f in os.listdir(pub_dir):
                    if f.endswith('.ma'):
                        v = parse_version(f)
                        if v and v > best_ver:
                            best_ver, best_file = v, f
                if best_file:
                    full_path = os.path.join(pub_dir, best_file)
                    cmds.file(full_path, reference=True, namespace=f'{task}_ref')
                    cmds.inViewMessage(msg=f'<span style=\"color:#00ff88;\">Loaded: {best_file}</span>', pos='topCenter', fade=True)
                else:
                    cmds.warning('OmniPipe: No versioned files found in publish directory.')
        except Exception as e:
            cmds.warning(f'OmniPipe Load Latest error: {e}')
"""


def _shelf_cmd_doctor():
    return """
import subprocess, sys, os
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
)))) if '__file__' in dir() else ''
# Fallback: use the omnipipe module path
if not repo_root:
    import omnipipe
    repo_root = os.path.dirname(os.path.dirname(omnipipe.__file__))
print('[OmniPipe] Running doctor check...')
os.system(f'{sys.executable} -m omnipipe doctor')
"""


def _show_license_blocked_dialog(msg):
    """Show a non-blocking warning in Maya's viewport."""
    import maya.cmds as cmds
    cmds.confirmDialog(
        title="OmniPipe — License Error",
        message=(
            f"License validation failed:\n\n{msg}\n\n"
            "OmniPipe shelf buttons will be disabled.\n"
            "Contact your Pipeline Admin to resolve."
        ),
        button=["OK"],
        defaultButton="OK",
        icon="critical",
    )
    cmds.warning(f"[OmniPipe] LICENSE BLOCKED: {msg}")


# ── Main entry point (called by userSetup.py) ─────────────────────────────────

def bootstrap():
    """
    Main startup routine. Called via cmds.evalDeferred() from userSetup.py
    so Maya's UI is fully loaded before we touch shelves.
    """
    _inject_omnipipe_path()

    from omnipipe.core.logger import setup_logger
    log = setup_logger("omnipipe.maya.startup")

    log.info("=" * 60)
    log.info("OmniPipe Maya Startup — initializing…")
    log.info("=" * 60)

    # ── License check ─────────────────────────────────────────────────────
    valid, msg = _validate_license()

    if valid:
        log.info("License OK: %s", msg)
        print(f"[OmniPipe] ✅ {msg}")
        _create_shelf()
    else:
        log.error("License FAILED: %s", msg)
        print(f"[OmniPipe] ❌ {msg}")
        _show_license_blocked_dialog(msg)

    log.info("OmniPipe Maya startup complete.")
