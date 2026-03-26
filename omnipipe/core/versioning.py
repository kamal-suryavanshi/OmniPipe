import os
import re
from typing import Optional
from omnipipe.core.logger import setup_logger

log = setup_logger("omnipipe.versioning")

# Industry standard versioning regex — matches "_v001", "_v0234" etc.
VERSION_REGEX = re.compile(r"_v(\d{3,4})")


def parse_version(filename: str) -> Optional[int]:
    """
    Extracts the version integer from a filename (e.g. 'model_v003.ma' → 3).
    Returns None if no version string is found.
    """
    match = VERSION_REGEX.search(filename)
    if match:
        v = int(match.group(1))
        log.debug("parse_version('%s') → %d", filename, v)
        return v
    log.debug("parse_version('%s') → no version token found", filename)
    return None


def format_version(version: int, padding: int = 3) -> str:
    """Formats an integer into a zero-padded version string (e.g. 3 → 'v003')."""
    return f"v{str(version).zfill(padding)}"


def get_latest_version(directory: str, base_name: str, extension: str) -> int:
    """
    Scans a directory for files matching base_name + version pattern + extension.
    Returns the highest version found, or 0 if none exist.
    """
    if not os.path.exists(directory):
        log.warning("get_latest_version: directory does not exist: %s", directory)
        return 0

    highest = 0
    scanned = 0
    for fname in os.listdir(directory):
        if fname.startswith(base_name) and fname.endswith(extension):
            scanned += 1
            v = parse_version(fname)
            if v and v > highest:
                highest = v

    log.debug("get_latest_version('%s', '%s', '%s') — scanned %d file(s), highest v=%d",
              directory, base_name, extension, scanned, highest)
    return highest


def get_next_available_path(directory: str, base_name: str, extension: str) -> str:
    """
    Safely computes the next logical versioned path in a directory.
    If the latest on disk is v005, returns the full path for v006.
    """
    latest   = get_latest_version(directory, base_name, extension)
    next_v   = format_version(latest + 1)
    filename = f"{base_name}_{next_v}{extension}"
    path     = os.path.join(directory, filename)
    log.info("get_next_available_path: latest=v%03d → next='%s'", latest, path)
    return path
