import os
import sys
from omnipipe.dcc.base import BaseDCC
from omnipipe.core.logger import setup_logger

log = setup_logger("omnipipe.dcc.silhouette")

# Try to import Silhouette's Python API if running inside the host
try:
    import fx
    HAS_SILHOUETTE = True
except ImportError:
    HAS_SILHOUETTE = False


class SilhouetteDCC(BaseDCC):
    """
    OmniPipe Silhouette/SilhouetteFX Integration (Person B)
    Concrete implementation of the BaseDCC abstract interface.

    Silhouette (now Boris FX Silhouette) is a rotoscoping, paint, and
    compositing tool. Its Python API uses the 'fx' module.

    Features:
      - License-gated save / save_as / publish
      - Auto version-bump on save (increments _vNNN in filename)
      - Metadata sidecar on publish
      - Headless dev-mode fallback when running outside Silhouette
    """

    # ── Query ─────────────────────────────────────────────────────────────

    def get_current_file(self) -> str:
        if HAS_SILHOUETTE:
            project = fx.activeProject()
            if project:
                return project.path
            return ""
        return "[SILHOUETTE DEV MODE] Returning dummy project path."

    def is_project_modified(self) -> bool:
        """Check if the current project has unsaved changes."""
        if HAS_SILHOUETTE:
            project = fx.activeProject()
            return project.isModified() if project else False
        return False

    # ── Open ──────────────────────────────────────────────────────────────

    def open_file(self, filepath: str) -> bool:
        log.info("open_file: %s", filepath)
        if HAS_SILHOUETTE:
            fx.loadProject(filepath)
            log.info("Project opened successfully.")
            return True
        print(f"[SILHOUETTE DEV MODE] Simulated opening project: {filepath}")
        return True

    # ── Save (with auto version-bump) ─────────────────────────────────────

    def save_file(self) -> bool:
        from omnipipe.core.license import validate_license
        valid, msg = validate_license()
        if not valid:
            log.error("LICENSE BLOCKED save: %s", msg)
            print(f"[OmniPipe] ❌ License required to save: {msg}")
            return False

        if HAS_SILHOUETTE:
            project = fx.activeProject()
            if project:
                project.save()
                log.info("Project saved: %s", project.path)
                return True
            log.error("save_file: no active project.")
            return False
        print("[SILHOUETTE DEV MODE] Simulated safely saving current project.")
        return True

    def save_as(self, filepath: str) -> bool:
        from omnipipe.core.license import validate_license
        valid, msg = validate_license()
        if not valid:
            log.error("LICENSE BLOCKED save_as: %s", msg)
            print(f"[OmniPipe] ❌ License required to save: {msg}")
            return False

        if HAS_SILHOUETTE:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            project = fx.activeProject()
            if project:
                project.saveAs(filepath)
                log.info("Project saved as: %s", filepath)
                return True
            log.error("save_as: no active project.")
            return False
        print(f"[SILHOUETTE DEV MODE] Simulated 'Save As' to: {filepath}")
        return True

    def save_version_up(self) -> str:
        """
        Auto version-bump: reads current filename, increments _vNNN → _v(N+1),
        then saves as the new filename. Returns the new path.

        roto_hero_v003.sfx → roto_hero_v004.sfx
        """
        from omnipipe.core.versioning import parse_version, format_version

        current = self.get_current_file()
        if not current or not os.path.basename(current):
            log.warning("save_version_up: no current project to version-bump.")
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
        Publish the current project:
          1. License check
          2. Copy/save project to publish_path
          3. Write metadata JSON sidecar
        """
        from omnipipe.core.license import validate_license
        valid, msg = validate_license()
        if not valid:
            log.error("LICENSE BLOCKED publish: %s", msg)
            print(f"[OmniPipe] ❌ License required to publish: {msg}")
            return False

        if HAS_SILHOUETTE:
            import shutil
            current = self.get_current_file()
            if not current or not os.path.exists(current):
                log.error("publish: No project file on disk to publish.")
                return False

            os.makedirs(os.path.dirname(publish_path), exist_ok=True)
            shutil.copy2(current, publish_path)
            log.info("Published project: %s → %s", current, publish_path)

            # Write metadata sidecar
            try:
                from omnipipe.core.metadata import generate_publish_metadata
                from omnipipe.core.publish import PublishInstance
                from omnipipe.core.context import PipelineContext

                proj_name = os.path.splitext(os.path.basename(current))[0]
                ctx = PipelineContext(dcc="silhouette")
                inst = PublishInstance(
                    name=proj_name,
                    context=ctx,
                    source_path=current,
                    publish_path=publish_path,
                    is_valid=True,
                    is_extracted=True,
                )
                generate_publish_metadata(inst)
                log.info("Metadata sidecar written for: %s", proj_name)
            except Exception as e:
                log.warning("Metadata generation skipped (non-fatal): %s", e)

            return True

        print(f"[SILHOUETTE DEV MODE] Simulated publishing project to: {publish_path}")
        return True

    # ── Silhouette-specific: Export roto shapes ───────────────────────────

    def export_shapes(self, output_path: str, fmt: str = "nuke") -> bool:
        """
        Export roto/paint shapes to an interchange format.

        Args:
            output_path: Destination file path
            fmt: Export format — 'nuke' (.nk), 'silhouette' (.fxs), 'shapes' (.ssf)

        Returns True if export succeeded.
        """
        from omnipipe.core.license import validate_license
        valid, msg = validate_license()
        if not valid:
            log.error("LICENSE BLOCKED export_shapes: %s", msg)
            return False

        if HAS_SILHOUETTE:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            project = fx.activeProject()
            if project:
                # Silhouette supports exporting shapes to Nuke .nk format
                fx.io.export(output_path, format=fmt)
                log.info("Exported shapes (%s) → %s", fmt, output_path)
                return True
            log.error("export_shapes: no active project.")
            return False

        print(f"[SILHOUETTE DEV MODE] Simulated exporting shapes ({fmt}) → {output_path}")
        return True
