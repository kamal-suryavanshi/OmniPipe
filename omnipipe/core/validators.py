import os
import re
from abc import ABC, abstractmethod
from omnipipe.core.publish import PublishInstance

class BaseValidator(ABC):
    """
    Abstract interface for all Publishing Gatekeepers.
    Any custom studio rule must inherit from this module!
    """
    @property
    def name(self) -> str:
        return self.__class__.__name__
        
    @abstractmethod
    def validate(self, instance: PublishInstance) -> bool:
        """
        Return True if valid, or raise an Exception if the file violates rules.
        """
        pass

class FileExistsValidator(BaseValidator):
    """
    Ensures the DCC (Maya/Nuke) actually securely wrote the source file 
    to the hard drive before we attempt to verify or copy it.
    """
    def validate(self, instance: PublishInstance) -> bool:
        if not os.path.exists(instance.source_path):
            raise ValueError(f"[{self.name}] Source file missing from disk: {instance.source_path}")
        return True

class NamingConventionValidator(BaseValidator):
    """
    Enforces brutal naming convention checks.
    Prevents artists from saving files with spaces or uppercase characters
    that will break or corrupt Linux-based render farms.
    """
    def validate(self, instance: PublishInstance) -> bool:
        base_name = os.path.basename(instance.source_path)
        
        if " " in base_name:
            raise ValueError(f"[{self.name}] Spaces are strictly forbidden in pipeline filenames: '{base_name}'")
            
        # Ensure only alphanumeric boundaries, underscores, and dots
        if not re.match(r"^[a-zA-Z0-9_\.]+$", base_name):
            raise ValueError(f"[{self.name}] Invalid characters detected in filename: '{base_name}'")
            
        return True

class LicenseValidator(BaseValidator):
    """
    Gatekeeper that natively prevents any physical data extraction or metadata JSON 
    from writing to the pipeline repository if a secure cryptography license key is missing.
    """
    def validate(self, instance: PublishInstance) -> bool:
        from omnipipe.core.license import validate_license
        is_valid, msg = validate_license()
        if not is_valid:
            raise ValueError(f"[{self.name}] {msg}")
        return True
