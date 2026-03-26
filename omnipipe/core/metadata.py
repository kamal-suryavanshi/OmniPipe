import os
import json
import time
import getpass
from typing import Dict, Any
from omnipipe.core.publish import PublishInstance

def generate_publish_metadata(instance: PublishInstance) -> bool:
    """
    Core Person A Metadata logic (Phase 3).
    Forces every single DCC publish in the entire studio into identical .json tracking data.
    """
    if not instance.is_valid:
        # Prevent broken models from polluting the metadata tracker
        return False
        
    meta_path = instance.publish_path.replace(os.path.splitext(instance.publish_path)[1], ".json")
    
    payload = {
        "asset_name": instance.name,
        "author": getpass.getuser(),
        "timestamp": time.time(),
        "date": time.strftime('%Y-%m-%d %H:%M:%S'),
        "source": instance.source_path,
        "publish": instance.publish_path,
        "context": {
            "project": instance.context.project,
            "sequence": instance.context.sequence,
            "shot": instance.context.shot,
            "task": instance.context.task,
            "dcc": instance.context.dcc
        },
        "custom_attributes": instance.metadata
    }
    
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)
    with open(meta_path, "w") as f:
        json.dump(payload, f, indent=4)
        
    print(f"  [METADATA] Successfully wrote global tracking JSON to: {meta_path}")
    return True
