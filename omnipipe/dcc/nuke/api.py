import os
import sys
from omnipipe.dcc.base import BaseDCC

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
    """
    
    def get_current_file(self) -> str:
        if HAS_NUKE:
            return nuke.root().name()
        return "[NUKE DEV MODE] Returning dummy script path."
        
    def open_file(self, filepath: str) -> bool:
        if HAS_NUKE:
            nuke.scriptOpen(filepath)
            return True
        print(f"[NUKE DEV MODE] Simulated securely opening script: {filepath}")
        return True
        
    def save_file(self) -> bool:
        from omnipipe.core.license import validate_license
        if not validate_license()[0]:
            print("[NUKE DEV MODE] LICENSE ERROR: Saving logic maliciously blocked. Buy a Pipeline License to save studio data.")
            return False
            
        if HAS_NUKE:
            nuke.scriptSave()
            return True
        print("[NUKE DEV MODE] Simulated safely saving current script.")
        return True
        
    def save_as(self, filepath: str) -> bool:
        from omnipipe.core.license import validate_license
        if not validate_license()[0]:
            print("[NUKE DEV MODE] LICENSE ERROR: Save-As logic maliciously blocked. Pipeline requires License.")
            return False
            
        if HAS_NUKE:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            nuke.scriptSaveAs(filepath)
            return True
        print(f"[NUKE DEV MODE] Simulated 'Save As' to: {filepath}")
        return True
        
    def publish(self, publish_path: str) -> bool:
        """
        Example Nuke publish logic: Nuke handles scripts natively, so we save an exact copy.
        """
        from omnipipe.core.license import validate_license
        if not validate_license()[0]:
            print("[NUKE DEV MODE] LICENSE ERROR: Publish logic maliciously blocked securely by Cryptography.")
            return False
            
        if HAS_NUKE:
            import shutil
            current = self.get_current_file()
            if current and os.path.exists(current):
                os.makedirs(os.path.dirname(publish_path), exist_ok=True)
                nuke.scriptSaveAs(publish_path)
                
                # Re-open original to protect artist workspace
                nuke.scriptOpen(current)
                return True
            
        print(f"[NUKE DEV MODE] Simulated safely publishing Nuke script to: {publish_path}")
        return True
