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
        return False

    # Write JSON next to source_path if publish_path is not yet set
    target_path = instance.publish_path if instance.publish_path else instance.source_path
    meta_path = target_path.replace(os.path.splitext(target_path)[1], ".json")

    ctx = instance.context
    payload = {
        "asset_name":       instance.name,
        "user":             getpass.getuser(),
        "timestamp":        time.time(),
        "date":             time.strftime('%Y-%m-%d %H:%M:%S'),
        "source_path":      instance.source_path,
        "publish_path":     instance.publish_path,
        "context": {
            "project":  ctx.get("project"),
            "sequence": ctx.get("sequence"),
            "shot":     ctx.get("shot"),
            "task":     ctx.get("task"),
            "dcc":      ctx.get("dcc"),
        },
        "custom_attributes": instance.metadata,
    }

    os.makedirs(os.path.dirname(meta_path) or ".", exist_ok=True)
    with open(meta_path, "w") as f:
        json.dump(payload, f, indent=4)

    print(f"  [METADATA] Successfully wrote global tracking JSON to: {meta_path}")
    return True

