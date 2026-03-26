import os
import hmac
import hashlib
from typing import Tuple
from omnipipe.core.logger import setup_logger

log = setup_logger("omnipipe.license")

# In the compiled Nuitka binary this key resides in obfuscated C memory space.
_SECRET_KEY = b"OMNI_SECURE_DEV_KEY_992_X_ALPHA"

_DEFAULT_LIC_PATH = os.path.join(os.path.expanduser("~"), "omnipipe.lic")


def verify_signature(payload: str, signature: str) -> bool:
    """Cryptographically verifies payload against an HMAC-SHA256 hex signature."""
    expected = hmac.new(_SECRET_KEY, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    match = hmac.compare_digest(expected, signature)
    if not match:
        log.warning("Signature mismatch for payload '%s' — license tampered or invalid.", payload)
    return match


def validate_license(license_path: str = None) -> Tuple[bool, str]:
    """
    Reads ~/omnipipe.lic and cryptographically verifies the HMAC-SHA256 signature.
    Returns (is_valid: bool, status_message: str).
    """
    lic_path = license_path or _DEFAULT_LIC_PATH
    log.debug("Validating license at: %s", lic_path)

    if not os.path.exists(lic_path):
        msg = (f"FATAL LICENSE ERROR: No valid license file found at {lic_path}. "
               "Please contact your Pipeline Admin.")
        log.error(msg)
        return False, msg

    try:
        with open(lic_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if len(lines) < 2:
            msg = "FATAL LICENSE ERROR: Corrupted or malformed license file — expected 2 lines."
            log.error(msg)
            return False, msg

        payload   = lines[0]
        signature = lines[1]
        log.debug("License payload: '%s'", payload)

        if verify_signature(payload, signature):
            msg = f"LICENSED: '{payload}'"
            log.info("License validated successfully for studio: '%s'", payload)
            return True, msg

        msg = ("FATAL LICENSE ERROR: Cryptographic SHA256 signature mismatch — "
               "license is invalid or has been tampered with.")
        log.error(msg)
        return False, msg

    except Exception as e:
        msg = f"FATAL LICENSE ERROR: Could not parse license file '{lic_path}': {e}"
        log.error(msg)
        return False, msg
