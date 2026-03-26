import os
import re
from typing import Optional

# Industry standard versioning regex (e.g. matches "_v001", "_v0234")
VERSION_REGEX = re.compile(r'_v(\d{3,4})')

def parse_version(filename: str) -> Optional[int]:
    """
    Extracts the version integer from a filename (e.g., 'model_v003.ma' -> 3).
    Returns None if no version string is found.
    """
    match = VERSION_REGEX.search(filename)
    if match:
        return int(match.group(1))
    return None

def format_version(version: int, padding: int = 3) -> str:
    """Formats an integer strictly into a zero-padded string (e.g., 3 -> 'v003')."""
    return f"v{str(version).zfill(padding)}"

def get_latest_version(directory: str, base_name: str, extension: str) -> int:
    """
    Scans a directory on the network for files matching the base_name and 
    returns the absolute highest version found. Returns 0 if none exist.
    """
    if not os.path.exists(directory):
        return 0
        
    highest_version = 0
    for f in os.listdir(directory):
        if f.startswith(base_name) and f.endswith(extension):
            v = parse_version(f)
            if v and v > highest_version:
                highest_version = v
                
    return highest_version

def get_next_available_path(directory: str, base_name: str, extension: str) -> str:
    """
    Safely computes the next logical incremental versioned path in a directory.
    If the artist is on v005, this guarantees the return path is v006.
    """
    latest = get_latest_version(directory, base_name, extension)
    next_v = format_version(latest + 1)
    
    # E.g. char_model_sh010_v006.ma
    filename = f"{base_name}_{next_v}{extension}"
    return os.path.join(directory, filename)
