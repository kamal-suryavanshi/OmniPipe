import os
import re
from typing import List
from omnipipe.core.publish import PublishInstance
from omnipipe.core.logger import setup_logger

log = setup_logger("omnipipe.dependencies")

# Maya Ascii: captures file paths from `file -r ... "path/to/file.ma";`
MAYA_REF_REGEX = re.compile(r'file\s+.*?-r\s+.*?"([^"]+)";')

# Nuke: captures `file /path/to/sequence.%04d.exr` inside Read node blocks
NUKE_READ_REGEX = re.compile(r"^\s*file\s+([^\s]+)", re.MULTILINE)


def extract_dependencies(instance: PublishInstance) -> List[str]:
    """
    Reads the raw ASCII source of a Maya (.ma) or Nuke (.nk) file
    and extracts all upstream file references without opening the DCC.
    """
    dependencies: List[str] = []
    source_path = instance.source_path

    if not os.path.exists(source_path):
        log.warning("[Dependencies] Source file not on disk — cannot scan: %s", source_path)
        return dependencies

    ext = os.path.splitext(source_path)[1].lower()
    if ext not in (".ma", ".nk"):
        log.info("[Dependencies] Unsupported file type '%s' — skipping dependency scan.", ext)
        return dependencies

    log.info("[Dependencies] Scanning '%s' for upstream references (type: %s)…",
             instance.name, ext)

    try:
        with open(source_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if ext == ".ma":
            matches = MAYA_REF_REGEX.findall(content)
            log.debug("[Dependencies] Maya regex matched %d raw reference(s).", len(matches))
        else:  # .nk
            matches = NUKE_READ_REGEX.findall(content)
            log.debug("[Dependencies] Nuke regex matched %d raw reference(s).", len(matches))

        for match in matches:
            norm = os.path.normpath(match)
            dependencies.append(norm)
            log.debug("[Dependencies]   → %s", norm)

    except Exception as e:
        log.error("[Dependencies] FAILED to parse '%s': %s", source_path, e)
        return dependencies

    # Deduplicate while preserving insertion order
    seen: set = set()
    unique_deps = []
    for d in dependencies:
        if d not in seen:
            seen.add(d)
            unique_deps.append(d)

    if unique_deps:
        log.info("[Dependencies] %d unique upstream reference(s) found in '%s'.",
                 len(unique_deps), instance.name)
    else:
        log.info("[Dependencies] No upstream references found in '%s'. "
                 "File may be standalone or reference pattern did not match.", instance.name)

    return unique_deps
