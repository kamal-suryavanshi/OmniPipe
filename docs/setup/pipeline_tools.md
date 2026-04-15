# Pipeline Tools Reference

This section documents all production-ready tools in OmniPipe. Each tool addresses a real-world deployment or artist workflow scenario.

---

## Tool Index

| Tool | Type | What it solves |
|---|---|---|
| [`init_studio.py --config`](#gap-1-headless-studio-init) | Script | Headless/CI studio init from intake YAML |
| [`install_workstation.py`](#gap-2-artist-workstation-installer) | Script | One-command artist machine setup |
| [`omnipipe create-shot`](#gap-3-create-shot-cli) | CLI | Add shots mid-project without re-running init |
| [NAS permission check](#gap-4-nas-permission-validation) | Built-in | Fail fast if NAS not writable before init |
| [`omnipipe doctor`](#gap-5-omnipipe-doctor) | CLI | Full environment health check |
| [`omnipipe.sh` / `omnipipe.bat`](#gap-6-os-launchers) | Launcher | Double-click or alias CLI entry point |
| [`omnipipe publish`](#omnipipe-publish) | CLI | Publish files through full pipeline lifecycle |
| [`omnipipe load-latest`](#omnipipe-load-latest) | CLI | Resolve latest published version per shot/task |
| [`install_maya_hook.py`](#maya-startup-hook) | Script | Installs OmniPipe shelf into Maya |
| [`install_nuke_hook.py`](#nuke-startup-hook) | Script | Installs OmniPipe menu into Nuke |

---

## Gap 1 — Headless Studio Init

**File:** `scripts/init_studio.py`

The `--config` flag allows fully automated, non-interactive deployments. Perfect for CI pipelines, remote setups, or deploying to multiple studios in one scripted run.

### Without `--config` (interactive)

```bash
python3 scripts/init_studio.py
# → prompts for each field one by one
```

### With `--config` (headless)

```bash
# Dry-run: see exactly what would be created
python3 scripts/init_studio.py \
    --config configs/client_intake.yaml \
    --dry-run

# Live run: creates the full folder hierarchy
python3 scripts/init_studio.py \
    --config configs/client_intake.yaml

# Force re-run over existing install (won't delete anything)
python3 scripts/init_studio.py \
    --config configs/client_intake.yaml \
    --force
```

### What `--config` enables

- Departments, DCCs, and asset types are read from the intake YAML — no hardcoded defaults
- Custom sequence/shot naming formats (`sq{:03d}`, `ep{:02d}`, etc.)
- All pipeline feature flags (`enable_dependency_tracking`, versioning padding, etc.)
- Safe to embed in a CI/CD pipeline or Ansible playbook

### Example intake file

See [`configs/client_intake_template.yaml`](../setup/intake_form_reference.md) for the full field reference.

---

## Gap 2 — Artist Workstation Installer

**File:** `scripts/install_workstation.py`

Run this **once on each new artist machine** to fully configure it for the pipeline. Takes approximately 2 minutes.

### Basic run

```bash
# Mac / Linux
python3 scripts/install_workstation.py

# Windows
python scripts\install_workstation.py
```

### With NAS license auto-copy

```bash
python3 scripts/install_workstation.py --nas-root /mnt/nas/projects
# → scans {nas_root}/*/_admin/licenses/omnipipe.lic and copies it to ~/omnipipe.lic
```

### Skip flags (for advanced/partial setups)

```bash
# Skip pip install (if deps already confirmed)
python3 scripts/install_workstation.py --skip-deps

# Skip smoke tests (headless/CI environments)
python3 scripts/install_workstation.py --skip-smoke

# Combine flags
python3 scripts/install_workstation.py \
    --nas-root /mnt/nas/projects \
    --skip-smoke
```

### What it checks

| Step | What happens |
|---|---|
| 1. Python version | Confirms 3.10+ — exits with error if below |
| 2. Dependencies | Runs `pip install -r requirements.txt` |
| 3. License copy | Copies `omnipipe.lic` from NAS `_admin/licenses/` |
| 4. License validation | Cryptographically verifies the HMAC-SHA256 signature |
| 5. Smoke test | Pings context resolver + Maya/Nuke DCC hooks |
| 6. Stamp | Writes `~/.omnipipe_workstation` — TD can verify remotely |

### Expected output

```
  ✅  Python 3.10.18 — meets minimum 3.10
  ✅  All pip dependencies satisfied.
  ✅  License copied from .../licenses/omnipipe.lic → ~/omnipipe.lic
  ✅  License valid — LICENSED: 'Acme VFX Studio'
  ✅  Context resolution smoke test PASSED
  ✅  MAYA DCC hook smoke test PASSED

  🎉  Workstation setup COMPLETE — this machine is pipeline-ready!
```

---

## Gap 3 — `create-shot` CLI

**Command:** `omnipipe create-shot`

Adds a **single new shot** to an existing project without re-running the full `init_studio.py`. Safe to run multiple times — skips folders that already exist.

### Usage

```bash
omnipipe create-shot STUDIO_ROOT PROJECT_CODE SEQUENCE SHOT [OPTIONS]
```

### Arguments

| Argument | Description | Example |
|---|---|---|
| `STUDIO_ROOT` | NAS root path | `/mnt/nas/projects` |
| `PROJECT_CODE` | Project folder name | `ACME_PROJ_2026` |
| `SEQUENCE` | Sequence folder name | `sq003` |
| `SHOT` | Shot folder name | `sh0050` |

### Options

| Option | Description |
|---|---|
| `--config FILE` | Path to `client_intake.yaml` for custom dept/DCC lists |
| `--dry-run` | Preview folder list without creating anything |

### Examples

```bash
# Basic: create sh0050 in sq003 using default departments and DCCs
omnipipe create-shot /mnt/nas/projects ACME_PROJ_2026 sq003 sh0050

# Dry-run: see what would be created
omnipipe create-shot /mnt/nas/projects ACME_PROJ_2026 sq004 sh0010 --dry-run

# With custom intake config (respects your dept/DCC list)
omnipipe create-shot /mnt/nas/projects ACME_PROJ sq002 sh0030 \
    --config configs/client_intake.yaml

# Windows equivalent
omnipipe create-shot Z:\projects ACME_PROJ sq001 sh0010
```

### What gets created

```
{STUDIO_ROOT}/{PROJECT_CODE}/sequences/{SEQUENCE}/{SHOT}/
├── _editorial/
├── work/
│   ├── maya/     {anim, comp, fx, lighting, …}
│   ├── nuke/     {anim, comp, fx, …}
│   ├── houdini/  …
│   └── blender/  …
├── publish/      (same tree as work/)
├── render/       {anim, comp, fx, …}
└── cache/        {anim, comp, fx, …}
```

---

## Gap 4 — NAS Permission Validation

This is **built into** `init_studio.py` and runs automatically before any folders are created. It is not a separate command.

### What it does

Before touching the disk, `init_studio.py` writes and immediately deletes a probe file at the studio root:

```
{studio_root}/.omnipipe_probe  →  written then deleted
```

### Failure scenarios

| Problem | Error message | Fix |
|---|---|---|
| NAS not mounted | `NAS root does NOT exist: /mnt/nas` | Mount the NAS drive first |
| User lacks write access | `Cannot write to NAS root: /mnt/nas` | Ask IT Admin to grant R/W |

### In dry-run mode

The probe write is skipped — the tool prints `[DRY RUN] Would check write permissions at: ...` and continues.

---

## Gap 5 — `omnipipe doctor`

**Command:** `omnipipe doctor`

A full environment health check. Run this after deploying to verify the machine is correctly configured. Returns exit code **0** if all checks pass, **non-zero** if any fail.

### Usage

```bash
omnipipe doctor [OPTIONS]
```

### Options

| Option | Description | Example |
|---|---|---|
| `--studio-root PATH` | NAS root to check mount + write access | `/mnt/nas/projects` |
| `--project CODE` | Project code to verify install stamp | `ACME_PROJ_2026` |

### Examples

```bash
# Quick check: just Python, imports, license, schema
omnipipe doctor

# Full check: includes NAS mount + write access + stamp
omnipipe doctor --studio-root /mnt/nas/projects --project ACME_PROJ_2026

# Windows
omnipipe doctor --studio-root Z:\projects --project ACME_PROJ_2026
```

### Checks performed

| # | Check | Pass | Fail |
|---|---|---|---|
| 1 | Python ≥ 3.10 | ✅ Version OK | ❌ Upgrade required |
| 2 | Core imports | ✅ All modules load | ❌ Missing dep or broken install |
| 3 | License present | ✅ `~/omnipipe.lic` found | ❌ File missing |
| 4 | License valid | ✅ HMAC signature OK | ❌ Tampered or expired |
| 5 | `schema.yaml` parseable | ✅ YAML valid | ❌ Syntax error |
| 6 | NAS mounted + writable | ✅ Probe write OK | ❌ Not mounted or read-only |
| 7 | Studio stamp present | ✅ `.omnipipe_stamp` found | ⚠️ Run `init_studio.py` first |

### Expected healthy output

```
  OmniPipe Doctor — Environment Health Check
  Platform : darwin  |  Python 3.10.18
  ─────────────────────────────────────────────────────────────────
  ✅  Python 3.10 — OK
  ✅  Import omnipipe.core.context
  ✅  Import omnipipe.core.publish
  ✅  Import omnipipe.core.license
  ✅  Import omnipipe.core.versioning
  ✅  License: LICENSED: 'Acme VFX Studio'
  ✅  schema.yaml parseable
  ✅  NAS root mounted and writable: /mnt/nas/projects
  ✅  Studio stamp found
  ─────────────────────────────────────────────────────────────────

  🎉  All checks PASSED — this machine is pipeline-healthy!
```

---

## Gap 6 — OS Launchers

Two launcher scripts are provided at the repo root — one for each platform.

### Mac / Linux: `omnipipe.sh`

```bash
# Make executable (one time only)
chmod +x omnipipe.sh

# Use directly
./omnipipe.sh doctor
./omnipipe.sh create-shot /mnt/nas PROJ sq001 sh0030
./omnipipe.sh context PROJ --sequence sq001 --shot sh0010

# Add a permanent alias (put in ~/.zshrc or ~/.bashrc)
alias omnipipe="/path/to/StudioPipeline/omnipipe.sh"
omnipipe doctor
```

### Windows: `omnipipe.bat`

```bat
rem From cmd.exe
omnipipe.bat doctor
omnipipe.bat create-shot Z:\projects PROJ sq001 sh0030

rem Works as just "omnipipe" if the folder is in your PATH
omnipipe doctor
```

### How the launcher resolves Python

Both launchers use this priority order:

```
1. ./bin/omnipipe-{mac|linux|win.exe}   ← compiled Nuitka binary (production)
2. ./venv/bin/python  (or .venv/)       ← virtualenv (development)
3. system python3 / python              ← global fallback
```

### Running with no arguments

Both launchers display a command reference menu when run with no args:

```bash
./omnipipe.sh
# → shows all available commands + admin script references
```

---

## `omnipipe publish`

**Command:** `omnipipe publish`

Publishes a source file through the complete pipeline lifecycle: **License → Validators → Extractors → Dependency Tracking → Metadata JSON**.

### Usage

```bash
omnipipe publish SOURCE [OPTIONS]
```

### Arguments

| Argument | Description | Example |
|---|---|---|
| `SOURCE` | Path to the source file to publish | `/mnt/nas/PROJ/work/maya/anim/hero_v003.ma` |

### Options

| Option | Short | Default | Description |
|---|---|---|---|
| `--project` | `-p` | *required* | Project code |
| `--sequence` | `-sq` | *required* | Sequence name |
| `--shot` | `-sh` | *required* | Shot name |
| `--task` | `-t` | *required* | Task name |
| `--dcc` | `-d` | `maya` | DCC name (`maya`, `nuke`, `silhouette`) |
| `--version` | `-v` | *auto-detected* | Version string (reads from filename if omitted) |
| `--track-deps` | | `False` | Enable upstream dependency scanning |
| `--dry-run` | | `False` | Validate only — no files written |

### Examples

```bash
# Publish with dependency tracking
omnipipe publish /mnt/nas/PROJ/work/maya/anim/hero_v003.ma \
  --project PROJ --sequence sq001 --shot sh0010 --task anim --track-deps

# Dry-run: validates everything but writes nothing
omnipipe publish /mnt/nas/PROJ/work/maya/anim/hero_v003.ma \
  --project PROJ --sequence sq001 --shot sh0010 --task anim --dry-run

# Override auto-detected version
omnipipe publish ./char_rig.ma \
  -p PROJ -sq sq001 -sh sh0010 -t rig --version v005
```

### Pipeline Phases

| Phase | What happens |
|---|---|
| License | Validates `~/omnipipe.lic` (blocks whole pipeline if invalid) |
| Validators | FileExists, NamingConvention checks |
| Extractors | EXR sequence, Playblast generation |
| Dependencies | Scans Maya/Nuke ASCII for `file -r` references (if `--track-deps`) |
| Metadata | Writes `{name}.json` sidecar with user, timestamp, source path, dependencies |

---

## `omnipipe load-latest`

**Command:** `omnipipe load-latest`

Scans the publish directory for a given shot/task/DCC and returns the path to the **highest versioned** file. Used by Nuke/Maya loaders to resolve references.

### Usage

```bash
omnipipe load-latest PROJECT SEQUENCE SHOT TASK [OPTIONS]
```

### Arguments

| Argument | Description | Example |
|---|---|---|
| `PROJECT` | Project code | `ACME_PROJ` |
| `SEQUENCE` | Sequence name | `sq001` |
| `SHOT` | Shot name | `sh0010` |
| `TASK` | Task name | `anim` |

### Options

| Option | Short | Default | Description |
|---|---|---|---|
| `--dcc` | `-d` | `maya` | DCC to filter by (determines file extension) |

### DCC Extension Map

| DCC | Extension scanned |
|---|---|
| `maya` | `.ma` |
| `nuke` | `.nk` |
| `houdini` | `.hip` |
| `blender` | `.blend` |
| `silhouette` | `.sfx` |

### Examples

```bash
# Latest Maya animation publish
omnipipe load-latest PROJ sq001 sh0010 anim --dcc maya

# Latest Nuke comp publish
omnipipe load-latest PROJ sq001 sh0010 comp --dcc nuke
```

### Expected Output

```
  Publish dir: /tmp/studio/PROJ/sequences/sq001/sh0010/publish/maya/anim

  📦  Latest publish: hero_anim_v008.ma  (v008)
  Full path: /tmp/studio/PROJ/sequences/sq001/sh0010/publish/maya/anim/hero_anim_v008.ma
```

---

## Maya Startup Hook

**Files:**
- `omnipipe/dcc/maya/startup.py` — startup logic (license check + shelf)
- `omnipipe/dcc/maya/userSetup.py` — Maya bootstrap file
- `scripts/install_maya_hook.py` — installer script

### What happens when Maya starts

```
Maya boots → executes userSetup.py
  → cmds.evalDeferred() waits for full UI load
  → omnipipe.dcc.maya.startup.bootstrap() runs:
      1. Injects repo root + vendor into sys.path
      2. Validates license (Layer 1: local .lic)
      3. Phone-home heartbeat (Layer 2: server)
      4. If valid → creates OmniPipe shelf (4 buttons)
      5. If invalid → shows warning dialog, shelf disabled
```

### OmniPipe shelf buttons

| Button | What it does |
|---|---|
| **OP Save** | License-gated `cmds.file(save=True)` |
| **OP Publish** | Runs `MayaDCC.publish()` → copies to publish path |
| **OP Load** | Prompts for shot context → references latest publish |
| **OP Doctor** | Runs `omnipipe doctor` in Script Editor |

### Installing the hook

```bash
# Default: install into Maya 2025
python3 scripts/install_maya_hook.py

# Specific Maya version
python3 scripts/install_maya_hook.py --maya-version 2024

# Custom scripts directory
python3 scripts/install_maya_hook.py --maya-dir /custom/maya/scripts
```

### Maya scripts directory by platform

| Platform | Path |
|---|---|
| macOS | `~/Library/Preferences/Autodesk/maya/{version}/scripts/` |
| Windows | `~/Documents/maya/{version}/scripts/` |
| Linux | `~/maya/{version}/scripts/` |

### What the installer does

1. Copies `userSetup.py` into Maya's scripts directory
2. Backs up any existing `userSetup.py` as `.py.bak_omnipipe`
3. Writes `OMNIPIPE_REPO_ROOT` into `Maya.env` so startup.py can find the repo

---

## Nuke Startup Hook

**Files:**
- `omnipipe/dcc/nuke/startup.py` — startup logic (license check + menu builder)
- `omnipipe/dcc/nuke/menu.py` — Nuke bootstrap file
- `scripts/install_nuke_hook.py` — installer script

### What happens when Nuke starts

```
Nuke boots → scans NUKE_PATH for menu.py → executes it
  → omnipipe.dcc.nuke.startup.bootstrap() runs:
      1. Injects repo root + vendor into sys.path
      2. Validates license (Layer 1 + Layer 2)
      3. If valid → builds OmniPipe menu bar (5 commands)
      4. If invalid → menu items show LOCKED + license error
```

### OmniPipe menu commands

| Command | Shortcut | What it does |
|---|---|---|
| **Save** | `Ctrl+S` | License-gated `nuke.scriptSave()` |
| **Save Version Up** | `Ctrl+Shift+S` | Auto `_v003` → `_v004` bump & save |
| **Publish** | — | Copies to publish path + metadata sidecar |
| **Load Latest (Read Node)** | — | Prompts for shot context → creates Read node |
| **Doctor** | — | Runs `omnipipe doctor` in console |

### Installing the hook

```bash
# Default install
python3 scripts/install_nuke_hook.py

# Specific Nuke version
python3 scripts/install_nuke_hook.py --nuke-version 14.0

# Custom plugin directory
python3 scripts/install_nuke_hook.py --nuke-dir /studio/nuke/plugins
```

### Nuke plugin directory

All platforms use `~/.nuke/` by default. The installer writes:
- `menu.py` — the OmniPipe bootstrap
- `init.py` — sets `OMNIPIPE_REPO_ROOT` environment variable

---

## Silhouette Startup Hook

**Files:**
- `omnipipe/dcc/silhouette/startup.py` — startup logic (license check + hook registry)

### What happens when Silhouette starts

```
Silhouette boots → invokes predefined scripts or user runs it
  → omnipipe.dcc.silhouette.startup.bootstrap() runs:
      1. Injects repo root + vendor into sys.path
      2. Validates license (Layer 1 + Layer 2)
      3. If valid → Adds OmniPipe menu to fx.menu() or binds to fx.bind()
      4. If invalid → Locks menu actions + shows license error
```

### OmniPipe menu/action hooks

| Action | What it does |
|---|---|
| **Save** | License-gated `fx.activeProject().save()` |
| **Save Version Up** | Auto `_v003` → `_v004` bump & save |
| **Publish** | Copies to publish path + metadata sidecar |
| **Export Shapes (Nuke)** | Exports Silhouette shapes to Nuke `.nk` format |
