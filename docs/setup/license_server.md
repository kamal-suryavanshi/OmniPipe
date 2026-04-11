# License Server

OmniPipe uses a **3-layer DRM system** to enforce studio licensing. This page documents Layer 2 — the central license server — and how all three layers work together.

---

## The 3-Layer Model

```
Layer 1 — Local .lic file           (every save/publish action)
Layer 2 — Phone-home heartbeat      (every DCC startup)
Layer 3 — Docker kill switch        (payment disputes only)
```

| Layer | When it fires | What it blocks | Managed by |
|---|---|---|---|
| **1 — Local `.lic`** | Every save + publish | Save/publish instantly | Pipeline TD |
| **2 — Phone-home** | DCC startup | Everything after grace expires | Person C |
| **3 — Kill switch** | Manual (admin) | All server-side pipeline ops | You (vendor) |

---

## Layer 2 — Phone-Home Heartbeat

Implemented in `omnipipe/core/license.py` → `phone_home()`.

### How it works

On DCC startup, `phone_home()` calls `POST /validate` on the license server with:
- `studio_id` — unique hash of the studio name
- `studio_name` — as it appears in the `.lic` file
- `machine_id` — hostname (for seat tracking)
- `dcc` — which DCC is starting (`maya`, `nuke`, `silhouette`)
- `client_sig` — HMAC re-signed locally (prevents replay attacks)

### Grace period

If the license server is **unreachable** (network outage, VPN down, studio offline):

```
First failure  → writes ~/.omnipipe_grace  → allows 7 days
During grace   → warns artist, pipeline continues
Day 8+         → blocks all DCC saves and publishes
Server back up → successful phone-home clears ~/.omnipipe_grace
```

This ensures a network blip never stops a production mid-shot.

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `OMNIPIPE_LICENSE_SERVER` | `https://license.omnipipe.io` | Point to self-hosted server |

```bash
# Use a local/dev license server
export OMNIPIPE_LICENSE_SERVER=http://localhost:8090
```

---

## License Server API

Runs in Docker on port **8090**. See `license_server/main.py`.

### `GET /health`
Liveness probe. Returns `{"status": "ok"}`.

### `POST /validate`
Called by `phone_home()` on DCC startup.

**Request body:**
```json
{
  "studio_id":   "abc123def456",
  "studio_name": "Acme VFX Studio",
  "machine_id":  "workstation-01",
  "dcc":         "nuke",
  "client_sig":  "<hmac-sha256>"
}
```

**Response (valid):**
```json
{"valid": true, "studio": "Acme VFX Studio", "days_left": 180, "grace_days": 7}
```

**Response (expired):**
```json
{"valid": false, "reason": "expired", "days_overdue": 5, "message": "Renew at omnipipe.io"}
```

### `POST /admin/issue` *(admin only)*
Issues a new license. Requires `X-Admin-Key` header.

```bash
curl -X POST http://localhost:8090/admin/issue \
  -H "X-Admin-Key: YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"studio_name": "Acme VFX Studio", "seats": 15, "plan": "professional"}'
```

### `POST /admin/revoke` *(admin only)*
Immediately revokes a studio license (kill switch).

```bash
curl -X POST http://localhost:8090/admin/revoke \
  -H "X-Admin-Key: YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"studio_id": "abc123def456", "reason": "Payment overdue 60 days"}'
```

### `GET /admin/list` *(admin only)*
Lists all issued licenses with status.

---

## Deploying the License Server

### Start with Docker Compose

```bash
# 1. Copy and fill in the env file
cp .env.example .env
# Edit .env with your secret keys

# 2. Start the license server only
docker compose up omnipipe-license -d

# 3. Verify health
curl http://localhost:8090/health
# → {"status": "ok", "server": "OmniPipe License Server", "version": "1.0.0"}
```

### Start the full studio stack

```bash
docker compose up -d
# Starts: omnipipe-license, omnipipe-api, kitsu, postgres
```

### Environment variables (`.env`)

| Variable | Required | Description |
|---|---|---|
| `OMNIPIPE_SECRET_KEY` | ✅ | Must match the key in `generate_license.py` |
| `OMNIPIPE_ADMIN_KEY` | ✅ | Used to authenticate `/admin/*` routes |
| `POSTGRES_PASSWORD` | ✅ | Database password |
| `KITSU_SECRET_KEY` | ✅ | Kitsu session signing secret |
| `NAS_HOST` | For NFS mounts | IP address of the NAS |
| `NAS_SHARE_PATH` | For NFS mounts | NFS export path on the NAS |

---

## Person C TODO List

- [ ] Replace the in-memory `LICENSES` dict with a SQLAlchemy + Postgres model
- [ ] Add Alembic migrations
- [ ] Implement JWT-based admin authentication (replace plain `X-Admin-Key`)
- [ ] Add rate limiting with `slowapi`
- [ ] Wire up email notifications (expiry warnings at 30/7/1 day)
- [ ] Build an admin web dashboard (React or simple Jinja2 templates)
- [ ] Connect to billing system (Stripe) for auto-renewal
