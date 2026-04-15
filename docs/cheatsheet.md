# CLI Cheatsheet

The OmniPipe CLI is built on **Typer**, making it inherently self-documenting. To get help on any command, simply append `--help` to it.

## Base Structure
```bash
python -m omnipipe [COMMAND] [OPTIONS]
```

## Available Commands

### 1. `init`
- **Who:** Pipeline TDs / Leads / Users
- **Description:** Initializes the pipeline environment on a new machine. Ensures all base configurations are loaded.
- **Valid Example:**
  ```bash
  python -m omnipipe init
  ```
  *(Expected Output: "Initializing OmniPipe...")*

### 2. `login`
- **Who:** Any Developer or Artist
- **Description:** Verifies pipeline connection against the central Asset Management DB (Kitsu). Reads credentials automatically from the root `.env` config file!
- **Valid Example:**
  ```bash
  python -m omnipipe login
  ```
  *(Expected Output: "Success! Connected to Asset Manager.")*

### 3. `context`
- **Who:** Developers & TDs
- **Description:** Dry-runs the Context System Path Resolver. It reads `configs/schema.yaml` and simulates exactly where Maya or Nuke files will physically save based on your inputs.
- **Valid Example:**
  ```bash
  # Test the path resolver for sequence 'seq01', shot 'sh010', task 'anim' in Maya
  python -m omnipipe context my_test_project --sequence seq01 --shot sh010 --task anim --dcc maya
  ```
  *(Expected Output: Resolves and prints exact physical paths for the Work File and Publish File)*

### 4. `test-dcc`
- **Who:** Person B / Developers
- **Description:** Directly pings the headless Maya or Nuke plugins outside the software to ensure the `BaseDCC` save/publish hooks execute safely without crashing.
- **Valid Example:**
  ```bash
  python -m omnipipe test-dcc nuke
  ```
  *(Expected Output: Simulated secure save and publish dummy terminal outputs)*

### 5. `publish`
- **Who:** Artists, TDs
- **Description:** Publishes a source file through the full OmniPipe pipeline — validates license, runs validators & extractors, tracks dependencies, writes metadata JSON.
- **Valid Examples:**
  ```bash
  # Publish a Maya animation file with full tracking
  python -m omnipipe publish /mnt/nas/PROJ/work/maya/anim/hero_v003.ma \
    --project PROJ --sequence sq001 --shot sh0010 --task anim --dcc maya --track-deps

  # Dry-run (validate only, no files written)
  python -m omnipipe publish /mnt/nas/PROJ/work/maya/anim/hero_v003.ma \
    --project PROJ --sequence sq001 --shot sh0010 --task anim --dry-run

  # Explicit version override
  python -m omnipipe publish ./char_rig.ma \
    --project PROJ -sq sq001 -sh sh0010 -t rig --version v005
  ```
  *(Auto-detects version from filename if `--version` is omitted)*

### 6. `load-latest`
- **Who:** Artists, TDs, DCC Loaders
- **Description:** Scans the publish directory for a given shot/task/DCC and prints the path to the latest versioned file. Used by Nuke/Maya loaders to resolve references.
- **Valid Examples:**
  ```bash
  # Find latest Maya anim publish
  python -m omnipipe load-latest PROJ sq001 sh0010 anim --dcc maya

  # Find latest Nuke comp publish
  python -m omnipipe load-latest PROJ sq001 sh0010 comp --dcc nuke
  ```
  *(Prints: `📦 Latest publish: hero_anim_v008.ma (v008)` + full path)*

### 7. `create-shot`
- **Who:** Production Coordinators, TDs
- **Description:** Creates a new shot's full folder tree (work/publish/render/cache) without re-running init_studio.
- **Valid Example:**
  ```bash
  python -m omnipipe create-shot /mnt/nas PROJ sq003 sh0050
  python -m omnipipe create-shot /mnt/nas PROJ sq003 sh0050 --dry-run  # preview only
  ```

### 8. `doctor`
- **Who:** TDs, System Admins
- **Description:** Runs a full post-deploy health check — Python version, imports, license, NAS mount, schema, studio stamp.
- **Valid Example:**
  ```bash
  python -m omnipipe doctor --studio-root /mnt/nas --project PROJ
  ```

---
_See `docs/setup/pipeline_tools.md` for the complete reference with all flags._
