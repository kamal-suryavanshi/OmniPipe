from typing import Dict, Any, List
from dataclasses import dataclass, field
from omnipipe.core.context import PipelineContext
from omnipipe.core.logger import setup_logger

log = setup_logger("omnipipe.publish")


@dataclass
class PublishInstance:
    """
    Represents a single immutable asset or file hitting the publish pipeline.
    Enforces strict standardization of metadata so artists can't save
    random messy files to the server.
    """
    name: str                                          # e.g. "character_geo"
    context: PipelineContext
    source_path: str
    publish_path: str = ""
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Internal pipeline state tracking
    is_valid: bool = False
    is_extracted: bool = False


class PublishEngine:
    """
    Central orchestrator: runs Validators → Extractors → Dependency Tracking → Metadata.
    All plugins are auto-registered at boot time; callers may also register extras.
    """

    def __init__(self, enable_tracking: bool = False):
        self.instances: List[PublishInstance] = []
        self.enable_tracking = enable_tracking

        log.debug("PublishEngine initialising (dependency_tracking=%s)", enable_tracking)

        from omnipipe.core.validators import FileExistsValidator, NamingConventionValidator, LicenseValidator
        from omnipipe.core.extractors import EXRSequenceExtractor, PlayblastExtractor

        self.validators = [LicenseValidator(), FileExistsValidator(), NamingConventionValidator()]
        self.extractors = [EXRSequenceExtractor(), PlayblastExtractor()]

        log.debug("Registered %d validator(s): %s",
                  len(self.validators), [v.name for v in self.validators])
        log.debug("Registered %d extractor(s): %s",
                  len(self.extractors), [e.name for e in self.extractors])

    def add_instance(self, instance: PublishInstance):
        log.debug("Added PublishInstance '%s' (source: %s)", instance.name, instance.source_path)
        self.instances.append(instance)

    def register_validator(self, validator):
        """Plugin injection point for additional Gatekeepers."""
        log.debug("Custom validator registered: %s", validator.name)
        self.validators.append(validator)

    def register_extractor(self, extractor):
        """Plugin injection point for additional Extractors."""
        log.debug("Custom extractor registered: %s", extractor.name)
        self.extractors.append(extractor)

    def run(self) -> bool:
        """
        Executes the full pipeline lifecycle per instance:
        Phase 1: Validations → Phase 2: Extractions → Phase 2.5: Dependency Tracking → Phase 3: Metadata
        """
        log.info("PublishEngine.run() — %d instance(s) queued", len(self.instances))

        if not self.instances:
            log.warning("PublishEngine.run() called with zero instances — nothing to publish.")
            return True

        for instance in self.instances:
            log.info("── Publishing: '%s' ──────────────────", instance.name)

            # ── Phase 1: Validators ────────────────────────────────────────────
            log.debug("[Phase 1] Running %d validators on '%s'", len(self.validators), instance.name)
            for validator in self.validators:
                try:
                    validator.validate(instance)
                    log.debug("  [✓] %s passed", validator.name)
                except Exception as e:
                    log.error("[Phase 1] Validator '%s' REJECTED '%s': %s",
                               validator.name, instance.name, e)
                    return False

            instance.is_valid = True
            log.info("[Phase 1] All validators passed for '%s'", instance.name)

            # ── Phase 2: Extractors ────────────────────────────────────────────
            log.debug("[Phase 2] Running %d extractor(s) on '%s'", len(self.extractors), instance.name)
            for extractor in self.extractors:
                try:
                    extractor.extract(instance)
                    log.debug("  [✓] Extractor '%s' completed", extractor.name)
                except Exception as e:
                    log.error("[Phase 2] Extractor '%s' FAILED on '%s': %s",
                               extractor.name, instance.name, e)
                    return False
            instance.is_extracted = True
            log.info("[Phase 2] All extractors completed for '%s'", instance.name)

            # ── Phase 2.5: Dependency Tracking (conditional) ──────────────────
            if self.enable_tracking:
                log.debug("[Phase 2.5] Dependency tracking enabled — scanning '%s'", instance.source_path)
                try:
                    from omnipipe.core.dependencies import extract_dependencies
                    deps = extract_dependencies(instance)
                    instance.metadata["dependencies"] = deps
                    log.info("[Phase 2.5] Found %d upstream dependency(ies) for '%s'",
                             len(deps), instance.name)
                except Exception as e:
                    log.warning("[Phase 2.5] Dependency scan failed for '%s' (non-fatal): %s",
                                instance.name, e)
            else:
                log.debug("[Phase 2.5] Dependency tracking disabled — skipping.")

            # ── Phase 3: Metadata JSON ─────────────────────────────────────────
            log.debug("[Phase 3] Writing metadata JSON for '%s'", instance.name)
            try:
                from omnipipe.core.metadata import generate_publish_metadata
                generate_publish_metadata(instance)
                log.info("[Phase 3] Metadata JSON committed for '%s'", instance.name)
            except Exception as e:
                log.error("[Phase 3] Metadata write FAILED for '%s': %s", instance.name, e)
                return False

        log.info("PublishEngine.run() completed successfully for all %d instance(s).", len(self.instances))
        return True
