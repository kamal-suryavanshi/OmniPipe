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
- **Description:** Initializes the pipeline environment on a new machine.

### 2. `login`
```bash
poetry run omnipipe login
```
- **Who:** Any Developer or Artist
- **Description:** Verifies pipeline connection against the central Asset Management DB (Kitsu). Reads credentials automatically from the root `.env` config file!

### 3. `context`
```bash
poetry run omnipipe context [project_name] --sequence seq01 --shot sh010 --task anim --dcc maya
```
- **Who:** Developers & TDs
- **Description:** Dry-runs the Context System Path Resolver. It reads `configs/schema.yaml` and simulates exactly where Maya or Nuke files will physically save.

---
_Note: More features (Publishing, Workfile Manager) will be added here as Day 4+ progresses!_
