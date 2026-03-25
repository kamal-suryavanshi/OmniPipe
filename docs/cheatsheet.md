# CLI Cheatsheet

The OmniPipe CLI is built on **Typer**, making it inherently self-documenting. To get help on any command, simply append `--help` to it.

## Base Structure
```bash
poetry run omnipipe [COMMAND] [OPTIONS]
```

## Available Commands

### 1. `init`
```bash
poetry run omnipipe init
```
- **Who:** Pipeline TDs / Leads / Users
- **Description:** Initializes the pipeline environment on a new machine or for a new artist. Ensures all base configurations are loaded.

### 2. `context`
```bash
poetry run omnipipe context [project_name] --sequence seq01 --shot sh010 --task anim --dcc maya
```
- **Who:** Developers & TDs
- **Description:** Dry-runs the Context System Path Resolver. It reads the local `configs/schema.yaml` and simulates exactly where Maya or Nuke workfiles and publishes will physically map on your machine or network. Use this when debugging new folder schemas.

---
_Note: More features (Publishing, Workfile Manager) will be added here as Day 3+ progresses!_
