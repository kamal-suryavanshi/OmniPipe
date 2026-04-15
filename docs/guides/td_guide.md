# Technical Director (TD) Guide

Welcome! This guide is explicitly for Technical Directors (TDs), Systems Administrators, or Pipeline Engineers tasked with deploying OmniPipe across a studio network. 

OmniPipe is designed to act as a **zero-install, centralized pipeline**. This means artists do not need to install Python packages, deal with paths, or configure environment variables. Every workstation boots off a central Studio NAS.

---

## 📋 Prerequisites
Before equipping the studio, ensure you have:
- **Central Storage:** A network-attached storage (NAS) or central file server mapped to a common letter/path across all artist machines (e.g., `Z:\`, `X:\`, or `/mnt/projects`).
- **Python 3.10+:** Installed on your central admin machine to deploy the initial files.
- **Admin Access:** To mount network drives and execute scripts.

---

## Phase 1: Initializing the Studio Root

OmniPipe requires a dedicated central folder on your NAS. You cannot just drop the repository anywhere; it must be "stamped" so the pipeline security wrappers recognize it as a valid OmniPipe ecosystem.

1. Clone or copy the `StudioPipeline` code onto your admin machine.
2. Run the initialization script to stamp your network directory and define the primary project constraints:
```bash
python scripts/init_studio.py --root "Z:\Projects" --project DEMO \
  --fps 24 --resolution 1920x1080 
```
*What this does:*
Outputs a hidden `.omnipipe_stamp` file validating the NAS drive. It also creates the `DEMO` project folder, adding standard pipeline structures inside (like `work/` and `publish/`).

---

## Phase 2: Building the Vendor Dependencies

Artists should never have to run `pip install`. We bundle every required third-party Python library into a network folder.

1. In your `StudioPipeline` code, run:
```bash
python scripts/build_vendor.py
```
2. This script downloads packages like `typer`, `rich`, and `gazu` (for Kitsu integration) into your central `StudioPipeline/vendor/` directory. When artist machines launch the pipeline, OmniPipe automatically appends this path to their `sys.path` in memory.

---

## Phase 3: Detailed Configuration (Schema & Intake)

OmniPipe relies entirely on configuration mapping. There are no hardcoded `C:\` paths in the codebase.

### The `schema.yaml`
Navigate to `configs/schema.yaml`. This file is the mathematical mapping engine for where files live across Mac, Linux, and Windows.

**Example Mount Setup:**
```yaml
mounts:
  nas_root: 
    windows: 'Z:\Projects'
    mac: '/Volumes/Projects'
    linux: '/mnt/projects'
```
*If a Mac artist clicks save, the PathResolver dynamically swaps out `Z:\` for `/Volumes/Projects` without the artist knowing.*

**Template Customization:**
You can rewrite exactly how files are named:
```yaml
templates:
  publish_file_maya: "{nas_root}/{project}/{sequence}/{shot}/publish/maya/{task}/{project}_{sequence}_{shot}_{task}_v{version}.ma"
```

### The `client_intake.yaml`
This is your actual production tracker. Fill this out to define your valid sequences and shots. 
```yaml
project: DEMO
sequences:
  sq010:
    fps: 24
    shots:
      sh0100:
        tasks: [anim, fx, comp]
```
*If an artist tries to publish a shot that is not in this document, the pipeline will actively block the save to prevent phantom directories.*

---

## Phase 4: Workstation Deployment (Onboarding Artists)

How do you get artists working? You do not need to install complex software on their machine.

1. **Mount the Network Drive:** Ensure the artist's computer has `Z:\Projects` (or the equivalent Mac/Linux mount) properly configured.
2. **Distribute the Connect Script:** Copy `scripts/install_workstation.py` to the artist's local computer.
3. **Execute:** The artist double-clicks or runs the install script.
```bash
python install_workstation.py --studio-root "Z:\Projects"
```
4. **Result:** The script modifies the artist's local `Maya.env` and Nuke plugins folder, pointing them securely back to your network NAS. 
5. *(Optional) Security License:* Have your artists place the generated `omnipipe.lic` file into their safe `~` (Home) directory, otherwise the `omnipipe publish` button will be locked out for them.

---

## Phase 5: Pipeline Updates

If you (the TD) edit a core Python file in `omnipipe/core/` and push it to the main branch, **how do artists get the update?**
- You pull the code down to the central Network Drive.
- Because all artists are mapped via the Workstation Connect script back to the NAS `__init__.py`, the next time they open Maya or Nuke, they instantly run the new code! Zero redeployment necessary.
