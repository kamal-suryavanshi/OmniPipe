import os
import sys
from omnipipe.dcc.base import BaseDCC

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
    """
    
    def get_current_file(self) -> str:
        if HAS_MAYA:
            return cmds.file(query=True, sceneName=True)
        return "[MAYA DEV MODE] Returning dummy scene path."
        
    def open_file(self, filepath: str) -> bool:
        if HAS_MAYA:
            cmds.file(filepath, open=True, force=True)
            return True
        print(f"[MAYA DEV MODE] Simulated securely opening: {filepath}")
        return True
        
    def save_file(self) -> bool:
        if HAS_MAYA:
            cmds.file(save=True, force=True)
            return True
        print("[MAYA DEV MODE] Simulated safely saving current file.")
        return True
        
    def save_as(self, filepath: str) -> bool:
        if HAS_MAYA:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            cmds.file(rename=filepath)
            cmds.file(save=True, type="mayaAscii")
            return True
        print(f"[MAYA DEV MODE] Simulated 'Save As' to: {filepath}")
        return True
        
    def publish(self, publish_path: str) -> bool:
        """
        Example Maya publish logic: Copy the exact scene dynamically to 
        the locked production server publish path via Python.
        """
        if HAS_MAYA:
            import shutil
            current = self.get_current_file()
            if current and os.path.exists(current):
                os.makedirs(os.path.dirname(publish_path), exist_ok=True)
                shutil.copy2(current, publish_path)
                return True
        
        print(f"[MAYA DEV MODE] Simulated safely publishing Maya asset to: {publish_path}")
        return True
