#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║     OmniPipe License Server  — license_server/main.py               ║
║                                                                      ║
║  A lightweight FastAPI service that acts as the central authority    ║
║  for OmniPipe license validation (Layer 2 of the 3-layer DRM).      ║
║                                                                      ║
║  Runs in Docker, managed by Person C.                                ║
║  Client machines phone home on DCC startup to confirm validity.      ║
║                                                                      ║
║  Person C TODO:                                                      ║
║    [ ] Replace in-memory store with Postgres (SQLAlchemy model)      ║
║    [ ] Add JWT-based admin authentication on /admin/* routes         ║
║    [ ] Add rate limiting (slowapi)                                   ║
║    [ ] Add email notification on expiry                              ║
║    [ ] Connect to Stripe / billing system for auto-renewal           ║
╚══════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import hmac
import hashlib
import os
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="OmniPipe License Server",
    description="Central license authority for OmniPipe studio deployments.",
    version="1.0.0",
)

# ── Shared secret (must match the key used by generate_license.py) ────────────
# Person C: move this to an env var / secrets manager (Vault, AWS Secrets Manager)
SECRET_KEY = os.getenv("OMNIPIPE_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")

# ── In-memory license store (Person C: replace with Postgres) ─────────────────
# Format: { studio_id: LicenseRecord }
LICENSES: dict[str, "LicenseRecord"] = {
    # Seed with a demo license for testing
    "demo-studio-001": {
        "studio_name":   "Demo VFX Studio",
        "studio_id":     "demo-studio-001",
        "seats":         10,
        "plan":          "professional",
        "issued_date":   "2026-01-01",
        "expiry_date":   "2026-12-31",
        "revoked":       False,
        "revoke_reason": None,
    }
}


# ── Schemas ───────────────────────────────────────────────────────────────────

class ValidateRequest(BaseModel):
    studio_id:   str
    studio_name: str
    machine_id:  str      # hostname or MAC — for seat tracking
    dcc:         str      # "maya" | "nuke" | "silhouette"
    client_sig:  str      # HMAC signature from the local .lic file


class IssueRequest(BaseModel):
    studio_name: str
    seats:       int      = 10
    plan:        str      = "professional"
    trial_days:  Optional[int] = None


class RevokeRequest(BaseModel):
    studio_id: str
    reason:    str


# ── Helpers ───────────────────────────────────────────────────────────────────

def _generate_studio_id(studio_name: str) -> str:
    return hashlib.sha256(studio_name.lower().encode()).hexdigest()[:16]


def _sign(studio_name: str) -> str:
    """Reproduce the HMAC used by generate_license.py."""
    return hmac.new(SECRET_KEY.encode(), studio_name.encode(), hashlib.sha256).hexdigest()


def _is_admin(x_admin_key: Optional[str]) -> bool:
    """Minimal admin auth — Person C: replace with JWT."""
    admin_key = os.getenv("OMNIPIPE_ADMIN_KEY", "ADMIN_SECRET_CHANGE_ME")
    return x_admin_key == admin_key


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Liveness probe — used by Docker HEALTHCHECK and load balancers."""
    return {"status": "ok", "server": "OmniPipe License Server", "version": "1.0.0"}


@app.post("/validate")
def validate_license(payload: ValidateRequest):
    """
    Called by omnipipe/core/license.py on every DCC startup (phone-home).

    Returns:
        {"valid": true,  "message": "...", "expiry": "YYYY-MM-DD", "grace_days": 7}
      OR
        {"valid": false, "message": "...", "reason": "expired|revoked|unknown"}
    """
    record = LICENSES.get(payload.studio_id)

    # Unknown studio
    if not record:
        return JSONResponse(status_code=200, content={
            "valid":   False,
            "reason":  "unknown",
            "message": f"Studio ID '{payload.studio_id}' not found. Contact support@omnipipe.io",
        })

    # Revoked
    if record["revoked"]:
        return JSONResponse(status_code=200, content={
            "valid":   False,
            "reason":  "revoked",
            "message": f"License revoked: {record['revoke_reason']}",
        })

    # Expired
    expiry = date.fromisoformat(record["expiry_date"])
    today  = date.today()
    if today > expiry:
        days_overdue = (today - expiry).days
        return JSONResponse(status_code=200, content={
            "valid":       False,
            "reason":      "expired",
            "days_overdue": days_overdue,
            "message":     f"License expired {days_overdue} day(s) ago. Renew at omnipipe.io",
        })

    # Valid
    days_left = (expiry - today).days
    return {
        "valid":      True,
        "studio":     record["studio_name"],
        "plan":       record["plan"],
        "seats":      record["seats"],
        "expiry":     record["expiry_date"],
        "days_left":  days_left,
        "grace_days": 7,   # client should tolerate 7 days of server unreachability
        "message":    f"LICENSED: '{record['studio_name']}' — {days_left} day(s) remaining",
    }


# ── Admin Routes (Person C: secure with JWT) ──────────────────────────────────

@app.post("/admin/issue")
def issue_license(payload: IssueRequest, x_admin_key: Optional[str] = Header(None)):
    """Issue a new studio license."""
    if not _is_admin(x_admin_key):
        raise HTTPException(status_code=403, detail="Forbidden")

    studio_id    = _generate_studio_id(payload.studio_name)
    issued_date  = date.today()
    expiry_date  = (
        issued_date + timedelta(days=payload.trial_days)
        if payload.trial_days
        else issued_date.replace(year=issued_date.year + 1)
    )

    LICENSES[studio_id] = {
        "studio_name":   payload.studio_name,
        "studio_id":     studio_id,
        "seats":         payload.seats,
        "plan":          payload.plan,
        "issued_date":   issued_date.isoformat(),
        "expiry_date":   expiry_date.isoformat(),
        "revoked":       False,
        "revoke_reason": None,
    }

    return {
        "issued":     True,
        "studio_id":  studio_id,
        "studio":     payload.studio_name,
        "expiry":     expiry_date.isoformat(),
        "hint":       f"Pass studio_id='{studio_id}' to the client for their config.",
    }


@app.post("/admin/revoke")
def revoke_license(payload: RevokeRequest, x_admin_key: Optional[str] = Header(None)):
    """Immediately revoke a studio license (nuclear option)."""
    if not _is_admin(x_admin_key):
        raise HTTPException(status_code=403, detail="Forbidden")

    record = LICENSES.get(payload.studio_id)
    if not record:
        raise HTTPException(status_code=404, detail="Studio not found")

    record["revoked"]       = True
    record["revoke_reason"] = payload.reason

    return {"revoked": True, "studio": record["studio_name"], "reason": payload.reason}


@app.get("/admin/list")
def list_licenses(x_admin_key: Optional[str] = Header(None)):
    """List all issued licenses with status."""
    if not _is_admin(x_admin_key):
        raise HTTPException(status_code=403, detail="Forbidden")

    today = date.today()
    result = []
    for sid, rec in LICENSES.items():
        expiry  = date.fromisoformat(rec["expiry_date"])
        status  = "revoked" if rec["revoked"] else ("expired" if today > expiry else "active")
        result.append({**rec, "status": status, "days_left": (expiry - today).days})

    return {"count": len(result), "licenses": result}


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
