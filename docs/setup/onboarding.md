# Studio Onboarding Guide

This page covers the complete end-to-end process for deploying OmniPipe at a new studio, from the initial client conversation through the first day an artist saves their first file.

---

## Overview

Onboarding a new studio is a **one-time** process that takes approximately 2–4 hours depending on the scale of the project. It is broken into four phases:

```
Phase 1 → Client Intake        (TD + Client, pre-setup)
Phase 2 → Environment Setup    (TD, machine/NAS preparation)
Phase 3 → Pipeline Init        (TD, init_studio.py)
Phase 4 → License & Handoff    (TD + Studio Supervisor)
```

---

## Phase 1 — Client Intake Form

Before touching any machine, collect a completed intake form from the client.

### What to Send

Send the client this file:
**`configs/client_intake_template.yaml`**

This is the single source of truth for all studio-specific pipeline settings.

### Minimum lead time

Allow **48 hours** for the client to return a completed form. Do not begin Phase 2 without it.

### What the form covers

| Section | What you're asking |
|---|---|
| `studio` | Studio legal name + project code (critical for license generation) |
| `filesystem` | NAS root path + OS platform (Windows vs Linux/Mac) |
| `project_structure` | Number of sequences, naming convention, shots per sequence |
| `departments` | Which tasks to pre-create (anim, comp, fx, lighting, etc.) |
| `dcc_software` | Which DCCs are licensed (Maya, Nuke, Houdini, etc.) |
| `asset_types` | char, prop, env, vehicle, fx, etc. |
| `technical` | FPS, frame padding, colour space, image format, resolution |
| `pipeline` | Feature flags (dependency tracking, versioning padding, etc.) |
| `contacts` | Pipeline TD, VFX Supervisor, IT Admin emails |

> **Tip:** Never skip the `contacts` section. You will need the IT Admin for NAS permissions and the Supervisor for license sign-off.

---

## Phase 2 — Environment Setup

Before running the init script, the following must be in place:

### 2.1 — Prerequisites

| Item | Windows | Mac / Linux |
|---|---|---|
| Python 3.10+ | [python.org](https://www.python.org) | `brew install python3` / system |
| Git | [git-scm.com](https://git-scm.com) | `brew install git` |
| NAS mount | Map network drive (e.g. `Z:\`) | `mount -t nfs ...` or SMB/Samba |
| NAS write permissions | IT Admin grants R/W to pipeline user | Same |

### 2.2 — Clone the repository

```bash
# On the Pipeline TD machine only (not artist workstations)
git clone https://github.com/your-studio/OmniPipe.git
cd OmniPipe
```

### 2.3 — Install dependencies

```bash
pip install -r requirements.txt
```

> All dependencies are also bundled in `omnipipe/vendor/` for air-gapped studios.  
> For fully offline setups: `pip install --no-index --find-links=omnipipe/vendor -r requirements.txt`

### 2.4 — Set the studio root environment variable (optional)

The `STUDIO_ROOT` env var overrides the path in `client_intake.yaml`. Useful for testing.

```bash
# Mac / Linux
export STUDIO_ROOT=/mnt/nas/projects

# Windows (PowerShell)
$env:STUDIO_ROOT = "Z:\projects"
```

---

## Phase 3 — Running the Studio Initialiser

### 3.1 — Copy and validate the intake form

Place the completed intake form at:
```
configs/client_intake.yaml
```

Do a quick sanity check before running:

```bash
# Verify YAML is valid (no syntax errors)
python3 -c "import yaml; yaml.safe_load(open('configs/client_intake.yaml'))"
```

### 3.2 — Dry-run first (always)

```bash
python3 scripts/init_studio.py --dry-run
```

Review the output. Confirm:

- [ ] The studio root path is correct
- [ ] The project code matches what the client expects
- [ ] The sequence and shot counts look right
- [ ] No unexpected departments or DCCs are listed

### 3.3 — Live run

```bash
# Mac / Linux
python3 scripts/init_studio.py

# Windows
python scripts\init_studio.py
```

Type `yes` when prompted to confirm. The script will:

1. Create the complete folder hierarchy on the NAS
2. Write `configs/studio_settings.yaml` with all client-specific settings
3. Copy `schema.yaml` into `{PROJECT_ROOT}/_admin/configs/`
4. Write a `.omnipipe_stamp` file to prevent accidental re-runs

### 3.4 — What gets created

```
{STUDIO_ROOT}/
└── {PROJECT_CODE}/
    ├── sequences/
    │   └── sq001/
    │       └── sh0010/
    │           ├── work/    {dcc}/ {task}/
    │           ├── publish/ {dcc}/ {task}/
    │           ├── render/  {task}/
    │           └── cache/   {task}/
    ├── assets/
    │   └── {asset_type}/ _template/ {work|publish}/ {dcc}/
    ├── editorial/
    ├── delivery/
    ├── dailies/
    ├── reference/
    ├── _admin/
    │   ├── licenses/        ← Store omnipipe.lic here for each workstation
    │   ├── scripts/
    │   ├── configs/         ← schema.yaml copy lives here
    │   └── logs/
    ├── _archive/
    └── .omnipipe_stamp      ← Prevents re-initialisation
```

> **Note:** The script only creates folders. It never deletes anything. Re-running with `--force` is safe — it skips already-existing directories.

---

## Phase 4 — License Generation & Handoff

### 4.1 — Generate the studio license key

Using the studio name **exactly as it appears** in `client_intake.yaml`:

```bash
python3 scripts/generate_license.py "Acme VFX Studio"
# → Writes ~/omnipipe.lic
```

This creates a cryptographically signed `.lic` file tied to the studio name.

### 4.2 — Deploy the license key

The `.lic` file must be present at `~/omnipipe.lic` on **every artist workstation**.

| Method | Command |
|---|---|
| Network share | Copy to `_admin/licenses/omnipipe.lic`, then symlink or copy to `~/` per machine |
| Remote deploy (SSH) | `scp omnipipe.lic artist@workstation01:~/` |
| IT MDM / Group Policy | Deploy via your IT provisioning system |

> **What happens without a license:**  
> Artists can still open the pipeline CLI and read/query context. They **cannot** save files or publish data.

### 4.3 — Smoke test on one artist machine

```bash
# Test Maya DCC hooks (no Maya required — uses dev mode)
python3 -m omnipipe test-dcc maya

# Test Nuke DCC hooks
python3 -m omnipipe test-dcc nuke

# Verify context resolution
python3 -m omnipipe context {PROJECT_CODE} --sequence sq001 --shot sh0010
```

---

## What's Still Missing (Recommended Next Steps)

The following are not yet built but should be considered for a production-grade deployment:

| Gap | Priority | Notes |
|---|---|---|
| `--config` flag on `init_studio.py` | 🔴 High | Read `client_intake.yaml` directly, skip all prompts for fully automated CI/remote setup |
| Artist workstation installer script | 🔴 High | One-click deploy: clone repo, install deps, copy license, test DCC hooks |
| `create-shot` CLI command | 🟡 Medium | Add individual shots post-init without re-running the full script |
| NAS permission validation | 🟡 Medium | Verify R/W access before creating folders (avoid silent permission failures) |
| `omnipipe doctor` health check | 🟡 Medium | Post-deploy verification: license OK? NAS mounted? Schema valid? |
| Email/Slack notification on publish | 🟢 Low | Notify supervisor when a shot is published |
| Studio settings UI | 🟢 Low | A simple web form to generate `client_intake.yaml` without editing raw YAML |
| Windows `.bat` / Mac `.sh` wrapper | 🟢 Low | One-double-click launcher for non-technical studio staff |

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---|---|---|
| `FileNotFoundError: Schema not found` | Wrong working directory | Always `cd` into the repo root first |
| `FATAL LICENSE ERROR` on save | `.lic` not at `~/omnipipe.lic` | Re-deploy the license key |
| `PermissionError` during folder creation | NAS permissions not set | Ask IT Admin to grant R/W |
| `ModuleNotFoundError: gazu` | Kitsu server not running | Expected — `omnipipe login` requires a live Kitsu instance |
| Folders created but empty | Init ran in `--dry-run` accidentally | Re-run without `--dry-run` |
| `.omnipipe_stamp` blocks re-run | Previous install detected | Use `--force` flag if intentional |
