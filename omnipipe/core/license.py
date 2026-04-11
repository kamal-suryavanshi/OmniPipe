import os
import hmac
import hashlib
import json
import datetime
from typing import Tuple
from omnipipe.core.logger import setup_logger

log = setup_logger("omnipipe.license")

# In the compiled Nuitka binary this key resides in obfuscated C memory space.
_SECRET_KEY = b"OMNI_SECURE_DEV_KEY_992_X_ALPHA"

_DEFAULT_LIC_PATH   = os.path.join(os.path.expanduser("~"), "omnipipe.lic")
_GRACE_FILE_PATH    = os.path.join(os.path.expanduser("~"), ".omnipipe_grace")
_GRACE_PERIOD_DAYS  = 7   # allow this many days if license server is unreachable

# Set this env var to point to a self-hosted or dev license server.
# Defaults to the production server.
_LICENSE_SERVER_URL = os.getenv(
    "OMNIPIPE_LICENSE_SERVER",
    "https://license.omnipipe.io"
)


# ── Layer 1: Local .lic cryptographic check ───────────────────────────────────

def verify_signature(payload: str, signature: str) -> bool:
    """Cryptographically verifies payload against an HMAC-SHA256 hex signature."""
    expected = hmac.new(_SECRET_KEY, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    match = hmac.compare_digest(expected, signature)
    if not match:
        log.warning("Signature mismatch for payload '%s' — license tampered or invalid.", payload)
    return match


def validate_license(license_path: str = None) -> Tuple[bool, str]:
    """
    Layer 1 — Reads ~/omnipipe.lic and cryptographically verifies the HMAC-SHA256 signature.
    Returns (is_valid: bool, status_message: str).
    Called on every save/publish action.
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


# ── Layer 2: Phone-home heartbeat to license server ───────────────────────────

def phone_home(studio_id: str, studio_name: str, dcc: str = "unknown") -> Tuple[bool, str]:
    """
    Layer 2 — Calls the OmniPipe license server on DCC startup to confirm the
    studio's subscription is still active, not revoked, and not expired.

    Uses a grace period: if the server is unreachable, the pipeline continues
    for up to GRACE_PERIOD_DAYS before enforcing offline.

    Returns (is_valid: bool, status_message: str).
    """
    try:
        import requests  # lazy import — not all environments have it
        import socket

        machine_id = socket.gethostname()
        validate_url = f"{_LICENSE_SERVER_URL}/validate"

        log.debug("Phone-home: contacting %s for studio '%s' (%s)", validate_url, studio_name, dcc)

        resp = requests.post(
            validate_url,
            json={
                "studio_id":   studio_id,
                "studio_name": studio_name,
                "machine_id":  machine_id,
                "dcc":         dcc,
                "client_sig":  hmac.new(
                    _SECRET_KEY,
                    studio_name.encode("utf-8"),
                    hashlib.sha256
                ).hexdigest(),
            },
            timeout=5,
        )

        data = resp.json()

        if data.get("valid"):
            msg = data.get("message", f"LICENSED: '{studio_name}'")
            log.info("Phone-home OK: %s | %d day(s) remaining", msg, data.get("days_left", 0))
            _clear_grace_file()
            return True, msg
        else:
            reason = data.get("reason", "unknown")
            msg = data.get("message", f"License invalid: {reason}")
            log.error("Phone-home REJECTED: %s", msg)
            return False, msg

    except Exception as e:
        log.warning("Phone-home failed (server unreachable?): %s — checking grace period.", e)
        return _apply_grace_period(studio_name)


# ── Grace period helpers ──────────────────────────────────────────────────────

def _apply_grace_period(studio_name: str) -> Tuple[bool, str]:
    """
    If the license server was unreachable, allow up to GRACE_PERIOD_DAYS of
    offline operation before blocking.
    """
    today = datetime.date.today()

    if os.path.exists(_GRACE_FILE_PATH):
        try:
            with open(_GRACE_FILE_PATH, "r") as f:
                grace_data = json.load(f)
            grace_start = datetime.date.fromisoformat(grace_data["grace_start"])
            days_elapsed = (today - grace_start).days

            if days_elapsed <= _GRACE_PERIOD_DAYS:
                remaining = _GRACE_PERIOD_DAYS - days_elapsed
                msg = (f"LICENSE SERVER UNREACHABLE — Grace period active: "
                       f"{remaining} day(s) remaining before enforcement.")
                log.warning(msg)
                return True, msg
            else:
                msg = (f"LICENSE GRACE PERIOD EXPIRED ({days_elapsed} days offline). "
                       f"Connect to the studio network to revalidate.")
                log.error(msg)
                return False, msg
        except Exception as e:
            log.error("Could not read grace file: %s", e)

    # First failure — write the grace file
    try:
        with open(_GRACE_FILE_PATH, "w") as f:
            json.dump({"grace_start": today.isoformat(), "studio": studio_name}, f)
        log.warning(
            "License server unreachable — grace period started (%d days). "
            "File written: %s", _GRACE_PERIOD_DAYS, _GRACE_FILE_PATH
        )
    except Exception as e:
        log.error("Could not write grace file: %s", e)

    return True, (f"LICENSE SERVER UNREACHABLE — Grace period started. "
                  f"{_GRACE_PERIOD_DAYS} day(s) allowed before enforcement.")


def _clear_grace_file():
    """Remove the grace file once a successful phone-home completes."""
    if os.path.exists(_GRACE_FILE_PATH):
        try:
            os.remove(_GRACE_FILE_PATH)
            log.debug("Grace file cleared after successful phone-home.")
        except Exception as e:
            log.warning("Could not remove grace file: %s", e)
