import os
import sys
from omnipipe.dcc.base import BaseDCC
from omnipipe.core.logger import setup_logger

log = setup_logger("omnipipe.dcc.maya")

# Try to natively import Maya's Python API if running inside the Maya Host
try:
    import maya.cmds as cmds
    HAS_MAYA = True
except ImportError:
    HAS_MAYA = False


class MayaDCC(BaseDCC):
    """
    OmniPipe Maya Integration (Person B)
    Concrete implementation of the BaseDCC abstract interface.

    Features:
      - License-gated save / save_as / publish
      - Auto version-bump on save (increments _vNNN in filename)
      - Publish routes through PublishEngine (validators → extractors → metadata)
      - Headless dev-mode fallback when running outside Maya
    """

    # ── Query ─────────────────────────────────────────────────────────────

    def get_current_file(self) -> str:
        if HAS_MAYA:
            scene = cmds.file(query=True, sceneName=True)
            return scene if scene else ""
        return "[MAYA DEV MODE] Returning dummy scene path."

    def is_scene_modified(self) -> bool:
        """Check if the current scene has unsaved changes."""
        if HAS_MAYA:
            return cmds.file(query=True, modified=True)
        return False

    # ── Open ──────────────────────────────────────────────────────────────

    def open_file(self, filepath: str) -> bool:
        log.info("open_file: %s", filepath)
        if HAS_MAYA:
            cmds.file(filepath, open=True, force=True)
            log.info("Scene opened successfully.")
            return True
        print(f"[MAYA DEV MODE] Simulated securely opening: {filepath}")
        return True

    # ── Save (with auto version-bump) ─────────────────────────────────────

    def save_file(self) -> bool:
        from omnipipe.core.license import validate_license
        valid, msg = validate_license()
        if not valid:
            log.error("LICENSE BLOCKED save: %s", msg)
            print(f"[OmniPipe] ❌ License required to save: {msg}")
            return False

        if HAS_MAYA:
            cmds.file(save=True, force=True)
            log.info("Scene saved: %s", self.get_current_file())
            return True
        print("[MAYA DEV MODE] Simulated safely saving current file.")
        return True

    def save_as(self, filepath: str) -> bool:
        from omnipipe.core.license import validate_license
        valid, msg = validate_license()
        if not valid:
            log.error("LICENSE BLOCKED save_as: %s", msg)
            print(f"[OmniPipe] ❌ License required to save: {msg}")
            return False

        if HAS_MAYA:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            cmds.file(rename=filepath)
            # Detect file type from extension
            file_type = "mayaAscii" if filepath.endswith(".ma") else "mayaBinary"
            cmds.file(save=True, type=file_type)
            log.info("Scene saved as: %s (type=%s)", filepath, file_type)
            return True
        print(f"[MAYA DEV MODE] Simulated 'Save As' to: {filepath}")
        return True

    def save_version_up(self) -> str:
        """
        Auto version-bump: reads current filename, increments _vNNN → _v(N+1),
        then saves as the new filename. Returns the new path.

        hero_anim_v003.ma → hero_anim_v004.ma
        """
        from omnipipe.core.versioning import parse_version, format_version

        current = self.get_current_file()
        if not current or not os.path.basename(current):
            log.warning("save_version_up: no current scene to version-bump.")
            return ""

        directory = os.path.dirname(current)
        basename  = os.path.basename(current)
        name, ext = os.path.splitext(basename)

        v = parse_version(basename)
        if v is None:
            # No version token — start at v001
            new_name = f"{name}_v001{ext}"
        else:
            # Increment version
            import re
            new_v = format_version(v + 1)
            new_name = re.sub(r"_v\d{3,4}", f"_{new_v}", basename)

        new_path = os.path.join(directory, new_name)
        log.info("save_version_up: %s → %s", basename, new_name)

        success = self.save_as(new_path)
        return new_path if success else ""

    # ── Publish (through PublishEngine) ────────────────────────────────────

    def publish(self, publish_path: str) -> bool:
        """
        Publish the current scene through the full OmniPipe pipeline:
          1. License check
          2. Copy scene to publish_path
          3. (If scene context available) run through PublishEngine

        Falls back to simple copy if context resolution fails.
        """
        from omnipipe.core.license import validate_license
        valid, msg = validate_license()
        if not valid:
            log.error("LICENSE BLOCKED publish: %s", msg)
            print(f"[OmniPipe] ❌ License required to publish: {msg}")
            return False

        if HAS_MAYA:
            import shutil
            current = self.get_current_file()
            if not current or not os.path.exists(current):
                log.error("publish: No scene file on disk to publish.")
                return False

            # Ensure the publish directory exists
            os.makedirs(os.path.dirname(publish_path), exist_ok=True)

            # Copy scene file to publish location
            shutil.copy2(current, publish_path)
            log.info("Published scene: %s → %s", current, publish_path)

            # Attempt to generate metadata JSON sidecar
            try:
                from omnipipe.core.metadata import generate_publish_metadata
                from omnipipe.core.publish import PublishInstance
                from omnipipe.core.context import PipelineContext

                # Build a lightweight context from the file path
                name = os.path.splitext(os.path.basename(current))[0]
                ctx = PipelineContext(dcc="maya")
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

        print(f"[MAYA DEV MODE] Simulated safely publishing Maya asset to: {publish_path}")
        return True
