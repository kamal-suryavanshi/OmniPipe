import os
import re
from abc import ABC, abstractmethod
from omnipipe.core.publish import PublishInstance
from omnipipe.core.logger import setup_logger

log = setup_logger("omnipipe.validators")


class BaseValidator(ABC):
    """Abstract interface for all Publishing Gatekeepers."""

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def validate(self, instance: PublishInstance) -> bool:
        """Return True if valid, raise ValueError if the file violates rules."""
        pass


class FileExistsValidator(BaseValidator):
    """
    Ensures the source file was actually written to disk before the
    pipeline attempts to copy or process it.
    """
    def validate(self, instance: PublishInstance) -> bool:
        log.debug("[%s] Checking source path exists: %s", self.name, instance.source_path)
        if not os.path.exists(instance.source_path):
            log.error("[%s] Source file MISSING from disk: %s", self.name, instance.source_path)
            raise ValueError(f"[{self.name}] Source file missing from disk: {instance.source_path}")
        log.debug("[%s] Source file confirmed on disk.", self.name)
        return True


class NamingConventionValidator(BaseValidator):
    """
    Enforces brutal naming convention rules.
    Prevents artists from saving files with spaces or non-alphanumeric chars
    that corrupt Linux-based render farms.
    """
    _PATTERN = re.compile(r"^[a-zA-Z0-9_\.]+$")

    def validate(self, instance: PublishInstance) -> bool:
        base_name = os.path.basename(instance.source_path)
        log.debug("[%s] Checking filename: '%s'", self.name, base_name)

        if " " in base_name:
            log.warning("[%s] Spaces detected in filename: '%s' — REJECTED", self.name, base_name)
            raise ValueError(f"[{self.name}] Spaces are strictly forbidden in pipeline filenames: '{base_name}'")

        if not self._PATTERN.match(base_name):
            log.warning("[%s] Invalid characters in filename: '%s' — REJECTED", self.name, base_name)
            raise ValueError(f"[{self.name}] Invalid characters detected in filename: '{base_name}'")

        log.debug("[%s] Filename '%s' is compliant.", self.name, base_name)
        return True


class LicenseValidator(BaseValidator):
    """
    Prevents any publish from proceeding when the cryptographic license
    key is absent or has been tampered with.
    """
    def validate(self, instance: PublishInstance) -> bool:
        log.debug("[%s] Verifying cryptographic license for '%s'", self.name, instance.name)
        from omnipipe.core.license import validate_license
        is_valid, msg = validate_license()
        if not is_valid:
            log.error("[%s] License INVALID — publish BLOCKED for '%s': %s",
                      self.name, instance.name, msg)
            raise ValueError(f"[{self.name}] {msg}")
        log.debug("[%s] License verified OK.", self.name)
        return True
