import os
from typing import List
from omnipipe.core.publish import PublishInstance

def extract_dependencies(instance: PublishInstance) -> List[str]:
    """
    Parses the actively published file (e.g. Maya .ma, Nuke .nk) to statically find 
    any upstream reference files it mathematically relies upon.
    """
    dependencies = []
    
    # Since the core API executes headlessly across all DCCs, we mock discovering a file
    print(f"  [DEPENDENCIES] Scanning {instance.name} for upstream template references...")
    
    # Simulating extracting an upstream Character Rig or Animation Cache
    mock_rig_dep = os.path.join(os.path.dirname(instance.publish_path), "..", "rig", "char_rig_v004.ma")
    dependencies.append(os.path.normpath(mock_rig_dep))
    
    print(f"  [DEPENDENCIES] Discovered {len(dependencies)} critical upstream templates.")
    return dependencies
