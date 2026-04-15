# QA & Tester Guide

Welcome! This guide is written for Quality Assurance (QA) testers, Production Coordinators, or Artists who need to test the pipeline *before* it rolls out to production. 

You don't need to be a programmer to follow this guide. We will walk you through exactly what you need, how to install it, and what buttons to click.

---

## 📋 Prerequisites
Before you start testing OmniPipe, please ensure your computer has:
1. **Python 3.10+**: Run `python --version` in your terminal to check. (Download from python.org if missing).
2. **At least one DCC**: Maya (2022+), Nuke (13+), or Silhouette installed.
3. **The License Key**: Place the `omnipipe.lic` file provided by your TD into your secure Home Directory (`~`).
4. **Access to the NAS**: You must be connected to the Studio NAS or Network Drive so you can reach the pipeline root.

---

## Step 1: Health Diagnostic

Before testing the creative apps, let's run the automated "Doctor" to double-check your computer's health.

1. Open your Terminal/Command Prompt.
2. Navigate to your local copy of StudioPipeline and type:
```bash
# Mac / Linux
./omnipipe.sh doctor

# Windows
omnipipe.bat doctor
```
3. A visual table will appear. Ensure that every item in the `Status` column has a green ✅. If you see a red ❌, report the error message to your TD!

---

## Step 2: Testing Maya Integrations

1. Run the local installer script on your terminal: `python scripts/install_maya_hook.py`
2. **Open Maya.**
3. Look at your toolbars near the top. You should see a brand new shelf tab called **OmniPipe**.
4. Create a simple sphere in the scene.
5. Click the **OP Save** button on the shelf. Because this is the first save, Maya will ask you where to put it. 
6. Move the sphere slightly.
7. Click the **OP Publish** button. 
   - **Verification:** A pop-up confirming that your file was automatically placed into the correct Pipeline Publish folder, and versioned up (e.g. `_v002`).

---

## Step 3: Testing Nuke Integrations

1. Run the installer: `python scripts/install_nuke_hook.py`
2. **Open Nuke.**
3. In the top menu bar, look for the new **OmniPipe** dropdown.
4. Add a `ColorBars` node.
5. Click **OmniPipe > Save Version Up** (or use `Ctrl+Shift+S`).
   - **Verification:** The script will automatically save and bump its version number.
6. Click **OmniPipe > Publish**.
   - **Verification:** It will take a snapshot and push it to the central server publish directory safely!

---

## Step 4: Command Line Tests (Advanced QA)

If you need to test the pipeline engine forcefully without opening DCC software:
1. Try publishing a dummy file from the terminal:
```bash
python -m omnipipe publish /path/to/test.ma --project DEMO --sequence sq01 --shot sh01 --task anim --dcc maya
```
2. Verify you see the green `🎉 Published successfully!` message and a dynamic progress bar.

---

## 📝 Reporting Bugs
If an app crashes or a button doesn't work, simply navigate to your local log folder (`~/omnipipe/logs/`). Grab the text files inside and send them to your Technical Director. They contain all the hidden stack trace data needed to fix the bug!
