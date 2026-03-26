import os
import json
import time
import getpass
from typing import Dict, Any
from omnipipe.core.publish import PublishInstance
from omnipipe.core.logger import setup_logger

log = setup_logger("omnipipe.metadata")


def generate_publish_metadata(instance: PublishInstance) -> bool:
    """
    Core Person A Metadata logic (Phase 3).
    Forces every single DCC publish in the entire studio into identical .json tracking data.
    """
    if not instance.is_valid:
        log.warning("generate_publish_metadata called on INVALID instance '%s' — skipping.",
                    instance.name)
        return False

    # Write JSON next to publish_path, or source_path if publish_path is not yet set
    target_path = instance.publish_path if instance.publish_path else instance.source_path
    meta_path = target_path.replace(os.path.splitext(target_path)[1], ".json")

    log.debug("Writing metadata JSON to: %s", meta_path)

    ctx = instance.context
    payload = {
        "asset_name":   instance.name,
        "user":         getpass.getuser(),
        "timestamp":    time.time(),
        "date":         time.strftime("%Y-%m-%d %H:%M:%S"),
        "source_path":  instance.source_path,
        "publish_path": instance.publish_path,
        "context": {
            "project":  ctx.get("project"),
            "sequence": ctx.get("sequence"),
            "shot":     ctx.get("shot"),
            "task":     ctx.get("task"),
            "dcc":      ctx.get("dcc"),
        },
        "custom_attributes": instance.metadata,
    }

    try:
        os.makedirs(os.path.dirname(meta_path) or ".", exist_ok=True)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)
        log.info("Metadata JSON committed: %s  (user=%s, ts=%s)",
                 meta_path, payload["user"], payload["date"])
    except OSError as e:
        log.error("FAILED to write metadata JSON for '%s': %s", instance.name, e)
        raise

    return True
