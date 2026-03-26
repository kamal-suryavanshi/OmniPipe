import os
import hmac
import hashlib
from typing import Tuple

# In a real C++ compiled AOT Nuitka build, this string resides violently obfuscated in the C memory space.
# It is extremely difficult to reverse-engineer out of the binary.
_SECRET_KEY = b"OMNI_SECURE_DEV_KEY_992_X_ALPHA"

def verify_signature(payload: str, signature: str) -> bool:
    """Cryptographically verifies an Ascii payload against a provided SHA256 hex signature."""
    expected_mac = hmac.new(_SECRET_KEY, payload.encode('utf-8'), hashlib.sha256).hexdigest()
    # compare_digest prevents timing attacks
    return hmac.compare_digest(expected_mac, signature)

def validate_license(license_path: str = None) -> Tuple[bool, str]:
    """
    Reads the physical omnipipe.lic file and verifies the cryptographic signature natively.
    Returns (is_valid, status_message).
    """
    if not license_path:
        # Default to the user's home OS directory so the pipeline runs globally
        license_path = os.path.join(os.path.expanduser("~"), "omnipipe.lic")
        
    if not os.path.exists(license_path):
        return False, f"FATAL LICENSE ERROR: No valid license file found at {license_path}. Please contact your Pipeline Admin."
        
    try:
        with open(license_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
        if len(lines) < 2:
            return False, "FATAL LICENSE ERROR: Corrupted and unreadable license file structure."
            
        # The secure license file structure is:
        # Line 1: Target Studio Client Name (Payload)
        # Line 2: HMAC-SHA256 Master Signature
        payload = lines[0]
        signature = lines[1]
        
        if verify_signature(payload, signature):
            return True, f"LICENSED STUDIO ROUTING: '{payload}'"
        else:
            return False, "FATAL LICENSE ERROR: Cryptographic SHA256 signature mismatch. The License is completely invalid or has been manually tampered with."
            
    except Exception as e:
        return False, f"FATAL LICENSE ERROR: Could not parse physical license file: {e}"
