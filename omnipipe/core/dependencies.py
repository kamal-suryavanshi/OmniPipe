import os
import re
from typing import List
from omnipipe.core.publish import PublishInstance

# Maya Ascii Reference Regex: matches commands like file -rdi 1 -ns "rig" ... "/path/to/file.ma";
MAYA_REF_REGEX = re.compile(r'file\s+.*?-r\s+.*?\"([^\"]+)\";')

# Nuke Read Node Regex: natively matches `file /path/to/sequence.%04d.exr` inside node blocks
NUKE_READ_REGEX = re.compile(r'^\s*file\s+([^\s]+)', re.MULTILINE)

def extract_dependencies(instance: PublishInstance) -> List[str]:
    """
    Dynamically parses the raw Ascii data of the physically published file 
    to mathematically extract exact upstream dependencies without needing the DCC open whatsoever.
    """
    dependencies = []
    source_path = instance.source_path
    
    if not os.path.exists(source_path):
        return dependencies
        
    print(f"  [DEPENDENCIES] Scanning raw Ascii source blocks for {instance.name}...")
        
    try:
        # Read the file purely as raw text (works for .ma and .nk)
        with open(source_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
            # 1. Parse Maya Ascii Dependencies
            if source_path.endswith(".ma"):
                matches = MAYA_REF_REGEX.findall(content)
                for match in matches:
                    dependencies.append(os.path.normpath(match))
                    
            # 2. Parse Nuke Script Dependencies
            elif source_path.endswith(".nk"):
                matches = NUKE_READ_REGEX.findall(content)
                for match in matches:
                    dependencies.append(os.path.normpath(match))
                    
    except Exception as e:
        print(f"  [DEPENDENCIES] Fatal error parsing raw file {source_path}: {e}")
        
    # Purge duplicates
    dependencies = list(set(dependencies))
    
    print(f"  [DEPENDENCIES] Intelligently parsed {len(dependencies)} upstream physical references natively from text strings.")
    return dependencies
