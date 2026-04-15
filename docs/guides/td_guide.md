# Technical Director (TD) Guide

Welcome! This guide is explicitly for Technical Directors (TDs), Systems Administrators, or Pipeline Engineers tasked with deploying OmniPipe across a studio network.

## 📋 Prerequisites
Before equipping the studio, ensure you have:
- **Central Storage:** A network-attached storage (NAS) or central file server mapped to a common letter/path across all artist machines (e.g., `Z:\` or `/mnt/projects`).
- **Python 3.10+:** Installed on your admin machine.
- **Admin Access:** To deploy license keys and workstation install scripts over the network.
- **Docker:** (Optional but recommended) For running the central License Server.

---

## Step 1: Initializing the Studio Root

OmniPipe requires a dedicated "Projects" folder on your NAS.
1. Run the initialization script to stamp the directory:
```bash
python scripts/init_studio.py --root /mnt/projects --project DEMO \
  --fps 24 --resolution 1920x1080 
```
*This creates the hidden `.omnipipe_stamp` file validating the NAS drive.*

## Step 2: Configuring the Schema

The `schema.yaml` file controls exactly where artist files are saved.
1. Open `configs/schema.yaml`
2. Adjust your mount templates:
```yaml
mounts:
  nas_root: 
    windows: 'Z:\Projects'
    mac: '/Volumes/Projects'
    linux: '/mnt/projects'
```
3. Customize your standard folder naming conventions under `directories`.

## Step 3: Setting Up Dependencies

OmniPipe is zero-install for artists, meaning all their modules load directly from the NAS!
1. Build the network dependency bundle:
```bash
python scripts/build_vendor.py
```
*This downloads libraries like `typer`, `gazu`, and `rich` into the `vendor/` folder, which is pushed to the pipeline root. Artists won't need to run `pip install`!*

## Step 4: Workstation Deployment

To attach artists to the pipeline:
1. Provide artists with the `install_workstation.py` script.
2. Share the secret `omnipipe.lic` file and have them place it in their home directory.
3. They will run the script, which automatically injects the hooks into Maya, Nuke, and Silhouette.

## Step 5: License Server (Optional)

If utilizing Layer 3 tracking:
1. Copy the `license_server/` folder to a secure Docker host.
2. Run `docker-compose up -d`.
3. Distribute the host IP to `configs/license.ini` so artists phone-home to your server.
