from typing import Optional
from omnipipe.dcc.base import BaseDCC

def get_dcc(dcc_name: str) -> Optional[BaseDCC]:
    """
    Central Factory Function to route and load the correct Headless API 
    for whatever host software is currently requesting it.
    """
    cmd = dcc_name.lower()
    
    if cmd == "maya":
        from omnipipe.dcc.maya.api import MayaDCC
        return MayaDCC()
        
    elif cmd == "nuke":
        from omnipipe.dcc.nuke.api import NukeDCC
        return NukeDCC()

    elif cmd == "silhouette":
        from omnipipe.dcc.silhouette.api import SilhouetteDCC
        return SilhouetteDCC()

    return None
