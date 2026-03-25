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

---
_Note: More features (Publishing, Workfile Manager) will be added here as Day 4+ progresses!_
