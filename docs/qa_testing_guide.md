# OmniPipe QA & End-User Testing Guide

Welcome to the OmniPipe testing team! This guide is written for Quality Assurance (QA) testers, Production Coordinators, or Artists who need to test the pipeline *before* it rolls out to the rest of the studio.

You don't need to be a programmer or a Technical Director (TD) to follow this guide. We will walk you through exactly what you need, how to install it, and what buttons to click.

---

## 🚀 Phase 1: Prerequisites

Before you can test OmniPipe, please make sure your computer has the following installed:

### 1. Python 3.10+
OmniPipe requires modern Python. 
- **Mac:** Download the [official macOS installer here](https://www.python.org/downloads/macos/) or open the Terminal app and type `brew install python` (if you have Homebrew).
- **Windows:** Download the [official Windows installer here](https://www.python.org/downloads/windows/). *Important: During install, make sure you check the box that says "Add Python to PATH" before hitting Install.*

*To check if you already have it:*
Open your Terminal (Mac) or Command Prompt (Windows) and type:  
`python --version` (or `python3 --version`). 
If it says `3.10` or higher, you are ready!

### 2. A Supported DCC (Creative App)
You must have at least one of these installed on your machine:
- **Maya** (2022 to 2025)
- **Nuke** (13.0 to 15.0)
- **Silhouette**

### 3. A Studio Drive or NAS (Optional but recommended)
OmniPipe relies on a "Studio Root" folder (like a NAS drive at `Z:\Projects` or `/mnt/projects`). If you don't have a NAS mounted, OmniPipe will safely use a temporary folder on your local drive (`/tmp/studio/` on Mac/Linux, or `C:\tmp\studio\` on Windows).

---

## 🛠️ Phase 2: Installing OmniPipe

As an artist or tester, you don't have to worry about complex code. Simply run the automated workstation installer!

1. Open your **Terminal** or **Command Prompt**.
2. Navigate to the folder where you saved the `StudioPipeline` code. For example:
   ```bash
   cd ~/Developer/StudioPipeline
   ```
3. Run the workstation installer:
   ```bash
   # On Mac / Linux:
   python3 scripts/install_workstation.py

   # On Windows:
   python scripts\install_workstation.py
   ```
4. **Read the Output:** The screen will show you a checklist of green ✅ checkmarks. It will automatically check your Python version, install any required packages, and try to find a valid license key. 
   *(Note: If it complains about a missing license, ask your TD for the `omnipipe.lic` file and place it in your User Home folder).*

---

## 🏥 Phase 3: The Doctor Check

Now let's make sure your computer is 100% healthy before testing the creative apps. We've built an automated "Doctor" that double-checks your environment.

1. In your Terminal, type:
   ```bash
   # Mac / Linux
   ./omnipipe.sh doctor

   # Windows
   omnipipe.bat doctor
   ```
2. You should see a beautiful visual table appear. Ensure that every item in the `Status` column has a green ✅. If you see a red ❌, stop here and report the error message to your TD!

---

## 🎨 Phase 4: Testing the Apps (DCCs)

Now for the fun part: testing inside the actual software! 

### Test A: Autodesk Maya
1. First, we need to inject OmniPipe into Maya. Run the Maya hook installer on your terminal:
   ```bash
   # Mac/Linux
   python3 scripts/install_maya_hook.py
   
   # Windows
   python scripts\install_maya_hook.py
   ```
2. **Open Maya.**
3. Look at your toolbars near the top. You should see a brand new shelf tab called **OmniPipe**.
4. Create a simple sphere in the scene.
5. Click the **OP Save** button on the shelf. Because this is the first save, Maya will ask you where to put it. *Manually* save it on your computer somewhere. 
6. Move the sphere slightly.
7. Click the **OP Publish** button. 
   - *What you should see:* A pop-up confirming that your file was automatically named, placed into the correct Pipeline Publish folder, and versioned up without you doing anything!

### Test B: Foundry Nuke
1. Open your Terminal and install the Nuke hook:
   ```bash
   # Mac/Linux
   python3 scripts/install_nuke_hook.py
   
   # Windows
   python scripts\install_nuke_hook.py
   ```
2. **Open Nuke.**
3. At the very top menu bar of Nuke, look for a new menu called **OmniPipe**.
4. Add a `Constant` node and a `ColorBars` node.
5. Click **OmniPipe > Save Version Up** (or use `Ctrl+Shift+S`).
   - *What you should see:* The script will save itself, automatically bumping its version (e.g. from `_v001.nk` to `_v002.nk`).
6. Click **OmniPipe > Publish**.
   - *What you should see:* It will take a snapshot and push it to the central server publish directory safely!

---

## 📝 Phase 5: QA Reporting

If you successfully completed all 4 phases, the pipeline is ready for production. 

**What to report if something breaks:**
We have built a custom "black-box" flight recorder. If an app crashes or a button doesn't work, you don't need to describe exactly what happened. 
Simply open this folder on your computer:
- `~/omnipipe/logs/`

Grab the text files inside that folder (which contain the timestamp of your crash) and Slack/email them to your Technical Director. They contain all the hidden data we need to fix the bug!
