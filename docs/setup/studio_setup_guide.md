# OmniPipe — Complete Studio Setup Guide

This is the master guide for deploying OmniPipe at any studio, from a blank machine to a fully operational pipeline. Follow all steps in order.

> **Guide status:** Person A (Core Pipeline) ✅ Complete · Person B (DCC Integrations) 🔜 Pending · Person C (Asset Management) 🔜 Pending

---

## Overview

```
Step 1 → Pre-requisites              (IT + Pipeline TD)
Step 2 → Clone & install OmniPipe   (Pipeline TD machine only)
Step 3 → Client intake form          (Client fills out)
Step 4 → Generate studio license     (Pipeline TD)
Step 5 → Initialize studio folders   (Pipeline TD)
Step 6 → Set up each artist machine  (Per workstation)
Step 7 → Verify the deployment       (Pipeline TD)
Step 8 → DCC integrations            (Person B — coming soon)
Step 9 → Asset Management / Kitsu    (Person C — coming soon)
```

---

## Step 1 — Pre-requisites

Before anything else, ensure the following are in place.

### Studio infrastructure

| Item | Requirement | Notes |
|---|---|---|
| NAS / shared storage | Mounted, network-accessible | Must be writable by the pipeline user |
| OS | Windows 10+ / macOS 12+ / Ubuntu 20.04+ | All three supported |
| Python | 3.10 or higher | [python.org](https://python.org) · macOS: `brew install python3` |
| Git | Any recent version | [git-scm.com](https://git-scm.com) |

### Verify Python

```bash
python3 --version
# Must output: Python 3.10.x or higher
```

### Verify NAS is mounted

```bash
# Mac / Linux — should list project folders
ls /mnt/nas/projects

# Windows — should open in Explorer
dir Z:\projects
```

---

## Step 2 — Clone & Install OmniPipe

Run this **once on the Pipeline TD machine only.** Artists get the pipeline through the workstation installer in Step 6.

```bash
# Clone the repo
git clone https://github.com/your-studio/OmniPipe.git StudioPipeline
cd StudioPipeline

# Create and activate a virtualenv (recommended)
python3 -m venv venv
source venv/bin/activate        # Mac / Linux
# or:  venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Verify the CLI works
python3 -m omnipipe --help
```

### Alternative: zero-install (offline studios)

All dependencies are bundled in `omnipipe/vendor/`. No internet required:

```bash
pip install --no-index --find-links=omnipipe/vendor -r requirements.txt
```

---

## Step 3 — Client Intake Form

Send the client this file to fill in before setup day:

```
configs/client_intake_template.yaml
```

Allow **48 hours** minimum for them to return it. Do not begin Step 4 without a completed form.

Full field reference: [Intake Form Reference](intake_form_reference.md)

Once completed, save it as:

```
configs/client_intake.yaml
```

Validate it runs without errors:

```bash
python3 -c "import yaml; yaml.safe_load(open('configs/client_intake.yaml'))"
# → no output = valid YAML
```

---

## Step 4 — Generate the Studio License

The license key is tied to the studio name **exactly as it appears** in `client_intake.yaml`.

```bash
# Read the studio name from the completed intake form first
grep "name:" configs/client_intake.yaml

# Generate the license key
python3 scripts/generate_license.py "Acme VFX Studio"
# → Writes ~/omnipipe.lic
```

> **Keep this `.lic` file secure.** It is cryptographically signed with a private key. Copy it to:
> ```
> {PROJECT_ROOT}/_admin/licenses/omnipipe.lic
> ```
> so the workstation installer can auto-deploy it to artist machines.

---

## Step 5 — Initialize Studio Folders

### 5a. Dry-run first (always)

```bash
python3 scripts/init_studio.py \
    --config configs/client_intake.yaml \
    --dry-run
```

Review the output. Confirm:
- [ ] Studio root path is correct
- [ ] Project code matches what the client expects
- [ ] Sequence and shot counts look right
- [ ] Listed departments and DCCs are correct

### 5b. Live run

```bash
# Mac / Linux
python3 scripts/init_studio.py --config configs/client_intake.yaml

# Windows
python scripts\init_studio.py --config configs\client_intake.yaml
```

Type `yes` to confirm. The script will:

1. Check NAS write permissions (probe file test)
2. Create the complete folder hierarchy on the NAS
3. Write `configs/studio_settings.yaml` for all client overrides
4. Copy `schema.yaml` snapshot to `{PROJECT_ROOT}/_admin/configs/`
5. Write `.omnipipe_stamp` to prevent accidental re-runs

### What gets built

```
{STUDIO_ROOT}/
├── _software/           ← DCC software landing zone
│   ├── maya/
│   ├── nuke/
│   └── houdini/
└── {PROJECT_CODE}/
    ├── sequences/
    │   └── sq001/
    │       └── sh0010/
    │           ├── work/    {dcc}/{task}/
    │           ├── publish/ {dcc}/{task}/
    │           ├── render/  {task}/
    │           └── cache/   {task}/
    ├── assets/
    │   └── {type}/_template/{work|publish}/{dcc}/
    ├── editorial/
    ├── delivery/
    ├── dailies/
    ├── reference/
    ├── _admin/
    │   ├── licenses/    ← deploy omnipipe.lic here
    │   ├── configs/     ← schema.yaml copy
    │   └── logs/
    ├── _archive/
    └── .omnipipe_stamp
```

### Adding a new shot later

When new shots are added mid-project, do **not** re-run `init_studio.py`. Use the CLI instead:

```bash
omnipipe create-shot /mnt/nas/projects ACME_PROJ sq003 sh0050
```

---

## Step 6 — Set Up Each Artist Workstation

Run this **once on every artist machine** that will use the pipeline.

```bash
# Basic (no NAS auto-copy — manual license deploy)
python3 scripts/install_workstation.py

# With NAS license auto-copy (recommended)
python3 scripts/install_workstation.py --nas-root /mnt/nas/projects

# Windows
python scripts\install_workstation.py --nas-root Z:\projects
```

The installer will:
1. Verify Python 3.10+
2. Install pip dependencies
3. Copy `omnipipe.lic` from `_admin/licenses/` → `~/omnipipe.lic`
4. Cryptographically validate the license
5. Run smoke tests (context path resolution + DCC hooks)
6. Write `~/.omnipipe_workstation` stamp

### Manual license deploy (if auto-copy fails)

```bash
# Copy the .lic file manually from the NAS
cp /mnt/nas/projects/{PROJECT_CODE}/_admin/licenses/omnipipe.lic ~/omnipipe.lic

# Windows (cmd.exe)
copy Z:\projects\ACME_PROJ\_admin\licenses\omnipipe.lic %USERPROFILE%\omnipipe.lic
```

### Make the launcher executable (Mac / Linux)

```bash
# Do this once on each machine
chmod +x /path/to/StudioPipeline/omnipipe.sh

# Optional: add a permanent alias
echo 'alias omnipipe="/path/to/StudioPipeline/omnipipe.sh"' >> ~/.zshrc
source ~/.zshrc
```

---

## Step 7 — Verify the Deployment

### 7a. Run the health check on each machine

```bash
omnipipe doctor \
    --studio-root /mnt/nas/projects \
    --project ACME_PROJ_2026
```

All 7 checks should show ✅. If any fail, see the [troubleshooting section](#troubleshooting).

### 7b. Run the full automated QA suite (TD machine only)

```bash
python3 scripts/qa_runner.py
```

Expected output:

```
  RESULTS: 9 tests run
  ✅ PASS: 9    ❌ FAIL: 0

  All Person A Core Validation tests passed! 🎉
```

### 7c. Smoke test a specific DCC hook

```bash
omnipipe test-dcc maya
omnipipe test-dcc nuke
```

### 7d. Test context path resolution

```bash
omnipipe context ACME_PROJ_2026 \
    --sequence sq001 \
    --shot sh0010 \
    --task anim \
    --dcc maya
```

---

## Step 8 — DCC Integrations 🔜

> **Status: Not yet implemented — Person B task.**

This step will cover wiring the OmniPipe save/publish hooks into the actual DCC APIs:

- **Maya** — `cmds.file()`, shelf button, script node auto-load
- **Nuke** — `nuke.scriptSave()`, custom panel, startup callback
- **Houdini** — `hou.hipFile.save()` override (if applicable)

Once Person B completes their implementation, this section will be updated with the full DCC-side installation guide.

---

## Step 9 — Asset Management / Kitsu 🔜

> **Status: Not yet implemented — Person C task.**

This step will cover connecting OmniPipe to the central asset management system:

- Kitsu server setup and project creation
- `omnipipe login` authentication
- Shot/asset status sync with publish metadata
- Review session integration

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---|---|---|
| `FileNotFoundError: Schema not found` | Wrong working directory | Always `cd` into the repo root |
| `LICENSE ERROR` on save/publish | `~/omnipipe.lic` missing | Re-deploy license from `_admin/licenses/` |
| `PermissionError` during folder creation | NAS permissions not set | IT Admin: grant R/W to the pipeline user |
| `ModuleNotFoundError` | Virtual env not activated | Run `source venv/bin/activate` |
| `Stamp found` blocks re-run | Previous install detected | Use `--force` flag if intentional |
| `QA test FAIL: dependency array missing` | `enable_dependency_tracking: false` | Expected — tracking is opt-in per `schema.yaml` |
| DCC hook shows `DEV MODE` output | Artist machine, no real DCC | Expected until Person B integrates |

---

## Quick Reference Card

```
─────────────── PIPELINE TD COMMANDS ────────────────────────────────────────

Setup (one time per studio):
  python3 scripts/generate_license.py "Studio Name"
  python3 scripts/init_studio.py --config configs/client_intake.yaml

Per workstation (one time):
  python3 scripts/install_workstation.py --nas-root /mnt/nas/projects

─────────────── DAILY PIPELINE COMMANDS ─────────────────────────────────────

Health check:
  omnipipe doctor --studio-root /mnt/nas/projects --project ACME_PROJ

Add a new shot:
  omnipipe create-shot /mnt/nas/projects ACME_PROJ sq003 sh0050

Test resolve paths:
  omnipipe context ACME_PROJ --sequence sq001 --shot sh0010 --task anim

Run full QA:
  python3 scripts/qa_runner.py

─────────────────────────────────────────────────────────────────────────────
```
