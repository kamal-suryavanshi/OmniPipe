import os
import sys
from omnipipe.dcc.base import BaseDCC
from omnipipe.core.logger import setup_logger

log = setup_logger("omnipipe.dcc.nuke")

# Try to natively import Nuke's Python API if running inside the Nuke Host
try:
    import nuke
    HAS_NUKE = True
except ImportError:
    HAS_NUKE = False


class NukeDCC(BaseDCC):
    """
    OmniPipe Nuke Integration (Person B)
    Concrete implementation of the BaseDCC abstract interface.

    Features:
      - License-gated save / save_as / publish
      - Auto version-bump on save (increments _vNNN in filename)
      - Metadata sidecar on publish
      - Load-latest: creates a Read node pointing at the latest publish
      - Headless dev-mode fallback when running outside Nuke
    """

    # ── Query ─────────────────────────────────────────────────────────────

    def get_current_file(self) -> str:
        if HAS_NUKE:
            name = nuke.root().name()
            return name if name and name != "Root" else ""
        return "[NUKE DEV MODE] Returning dummy script path."

    def is_script_modified(self) -> bool:
        """Check if the current script has unsaved changes."""
        if HAS_NUKE:
            return nuke.modified()
        return False

    # ── Open ──────────────────────────────────────────────────────────────

    def open_file(self, filepath: str) -> bool:
        log.info("open_file: %s", filepath)
        if HAS_NUKE:
            nuke.scriptOpen(filepath)
            log.info("Script opened successfully.")
            return True
        print(f"[NUKE DEV MODE] Simulated securely opening script: {filepath}")
        return True

    # ── Save (with auto version-bump) ─────────────────────────────────────

    def save_file(self) -> bool:
        from omnipipe.core.license import validate_license
        valid, msg = validate_license()
        if not valid:
            log.error("LICENSE BLOCKED save: %s", msg)
            print(f"[OmniPipe] ❌ License required to save: {msg}")
            return False

        if HAS_NUKE:
            nuke.scriptSave()
            log.info("Script saved: %s", self.get_current_file())
            return True
        print("[NUKE DEV MODE] Simulated safely saving current script.")
        return True

    def save_as(self, filepath: str) -> bool:
        from omnipipe.core.license import validate_license
        valid, msg = validate_license()
        if not valid:
            log.error("LICENSE BLOCKED save_as: %s", msg)
            print(f"[OmniPipe] ❌ License required to save: {msg}")
            return False

        if HAS_NUKE:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            nuke.scriptSaveAs(filepath)
            log.info("Script saved as: %s", filepath)
            return True
        print(f"[NUKE DEV MODE] Simulated 'Save As' to: {filepath}")
        return True

    def save_version_up(self) -> str:
        """
        Auto version-bump: reads current filename, increments _vNNN → _v(N+1),
        then saves as the new filename. Returns the new path.

        comp_beauty_v003.nk → comp_beauty_v004.nk
        """
        from omnipipe.core.versioning import parse_version, format_version

        current = self.get_current_file()
        if not current or not os.path.basename(current):
            log.warning("save_version_up: no current script to version-bump.")
            return ""

        directory = os.path.dirname(current)
        basename  = os.path.basename(current)
        name, ext = os.path.splitext(basename)

        v = parse_version(basename)
        if v is None:
            new_name = f"{name}_v001{ext}"
        else:
            import re
            new_v = format_version(v + 1)
            new_name = re.sub(r"_v\d{3,4}", f"_{new_v}", basename)

        new_path = os.path.join(directory, new_name)
        log.info("save_version_up: %s → %s", basename, new_name)

        success = self.save_as(new_path)
        return new_path if success else ""

    # ── Publish (with metadata sidecar) ───────────────────────────────────

    def publish(self, publish_path: str) -> bool:
        """
        Publish the current script:
          1. License check
          2. Copy/save script to publish_path
          3. Write metadata JSON sidecar
          4. Re-open original to protect artist workspace
        """
        from omnipipe.core.license import validate_license
        valid, msg = validate_license()
        if not valid:
            log.error("LICENSE BLOCKED publish: %s", msg)
            print(f"[OmniPipe] ❌ License required to publish: {msg}")
            return False

        if HAS_NUKE:
            current = self.get_current_file()
            if not current or not os.path.exists(current):
                log.error("publish: No script file on disk to publish.")
                return False

            os.makedirs(os.path.dirname(publish_path), exist_ok=True)
            nuke.scriptSaveAs(publish_path)
            log.info("Published script: %s → %s", current, publish_path)

            # Re-open original to protect artist workspace
            nuke.scriptOpen(current)

            # Write metadata sidecar
            try:
                from omnipipe.core.metadata import generate_publish_metadata
                from omnipipe.core.publish import PublishInstance
                from omnipipe.core.context import PipelineContext

                name = os.path.splitext(os.path.basename(current))[0]
                ctx = PipelineContext(dcc="nuke")
                inst = PublishInstance(
                    name=name,
                    context=ctx,
                    source_path=current,
                    publish_path=publish_path,
                    is_valid=True,
                    is_extracted=True,
                )
                generate_publish_metadata(inst)
                log.info("Metadata sidecar written for: %s", name)
            except Exception as e:
                log.warning("Metadata generation skipped (non-fatal): %s", e)

            return True

        print(f"[NUKE DEV MODE] Simulated safely publishing Nuke script to: {publish_path}")
        return True

    # ── Load Latest (B7: Create Read node) ────────────────────────────────

    def load_latest_as_read(self, publish_dir: str, file_pattern: str = "*.exr") -> bool:
        """
        Scan publish_dir for the latest versioned EXR sequence (or .nk),
        create a Nuke Read node pointing at it.

        Args:
            publish_dir: Directory to scan for published files
            file_pattern: Glob pattern to match (default: *.exr)

        Returns True if a Read node was created.
        """
        if not os.path.isdir(publish_dir):
            log.warning("load_latest_as_read: directory not found: %s", publish_dir)
            return False

        from omnipipe.core.versioning import parse_version

        best_file = None
        best_ver  = 0
        ext = os.path.splitext(file_pattern)[1] if "." in file_pattern else ".exr"

        for f in sorted(os.listdir(publish_dir)):
            if f.endswith(ext) or f.endswith(".nk"):
                v = parse_version(f)
                if v and v > best_ver:
                    best_ver  = v
                    best_file = f

        if not best_file:
            log.warning("load_latest_as_read: no versioned files found in %s", publish_dir)
            return False

        full_path = os.path.join(publish_dir, best_file)
        log.info("load_latest_as_read: latest = %s (v%03d)", best_file, best_ver)

        if HAS_NUKE:
            read_node = nuke.createNode("Read")
            read_node["file"].setValue(full_path.replace("\\", "/"))
            read_node["label"].setValue(f"OmniPipe v{best_ver:03d}")
            log.info("Created Read node: %s", full_path)
            return True

        print(f"[NUKE DEV MODE] Would create Read node: {full_path}")
        return True
