# Artist Usage Guide

Welcome to OmniPipe! This guide is written specifically for 3D Artists, Compositors, and Animators. 

OmniPipe is designed to be completely invisible until you need it. You don't have to navigate messy network folders, worry about naming your files correctly, or remember where the latest Animation render is stored. OmniPipe handles all the boring data management so you can focus strictly on creating amazing art!

---

## 📋 Prerequisites
Before you begin your day:
1. Ensure your studio TD or Coordinator has provided you with your secure `omnipipe.lic` file.
2. Ensure you have run the workstation installer (or wait for the `Install Complete ✅` message from your coordinator).
3. Ensure you are connected to the central Studio Server (e.g. `Z:\` drive on Windows or `/mnt/projects` on Mac).

---

## The UI: What Does OmniPipe Do?
When you are working in Maya, Nuke, or Silhouette, OmniPipe adds three magical buttons to your interface: **Save**, **Publish**, and **Load Latest**.

### 1. OmniPipe Save (OP Save)
**Purpose:** Saves your current "Work In Progress" file.
- If it is your **very first time** clicking save on a brand new empty scene, OmniPipe will ask you what your context is. You simply type the Project (e.g., `DEMO`), Sequence (`sq010`), Shot (`sh0100`), and Task (`anim`).
- Once you enter that, it will physically calculate the directory and move the file into the exact correct network folder, naming it `DEMO_sq010_sh0100_anim_v001`.
- If you have already saved before, clicking it again will just automatically bump up your version number (e.g. from `_v034` to `_v035`). It acts exactly like a smart "Save As".

### 2. OmniPipe Publish (OP Publish)
**Purpose:** Freezes an "approved" version of your work and ships it down the pipeline.
- Work files (`OP Save`) are messy. They are meant for daily WIP (Work in Progress) testing and exploring. Publishes (`OP Publish`) are permanent snapshots meant to be rendered or passed to other departments.
- When you click Publish, OmniPipe goes into lockdown:
    1. It scans your entire scene for messy geometry names or broken texture links.
    2. It forces a final Save.
    3. It tracks every asset you imported securely in the background.
    4. It takes a static snapshot and copies it to a locked, read-only `publish/` folder where Lighters and Compositors can safely grab it without fear of it being overwritten!

### 3. OmniPipe Load (Load Latest)
**Purpose:** Instantly grabs the absolute latest published file from an upstream department.
- Imagine you are a Compositor working in Nuke. The animator has been working all weekend and finalized version 47 (`_v047.ma`). 
- Instead of manually browsing massive NAS folders looking for it, you just click the **Load Latest** button and type in `anim`. OmniPipe will instantly drop the absolute newest Read node into your script, guaranteed to be the version the Director just approved.

---

## Example Workflow (Day in the Life)

**Morning (10:00 AM)**
- Open Maya. Create a basic Rig cycle. 
- Click **OP Save**. The file saves as `_v001.ma`.

**Afternoon (1:00 PM)**
- You add heavy physics simulations to the scene. 
- Click **OP Save**. It realizes you made changes and safely increments the file to `_v002.ma` so you don't lose the morning's progress.

**Evening (6:00 PM)**
- The shot looks amazing. The director says "Approved!"
- Click **OP Publish**. A green success message pops up. Boom — it is instantly securely delivered to the lighting and comp departments downstream. You can shut down your computer and go home.

---

## FAQ & Troubleshooting

**Q: Where did my file just go?**
A: You can always look at the top title bar of your Maya/Nuke window. OmniPipe automatically names your file based on the Studio naming convention and places it securely on the network drive (for example: `Z:\Projects\DEMO\sq010\sh0100\work\maya\anim\DEMO_sq010...`).

**Q: I got a red "VALIDATION ERROR" when publishing! What do I do?**
A: Read the pop-up carefully. OmniPipe stops you from publishing if you broke studio rules (for instance, leaving a space in a node name, or forgetting to link a background texture). Fix the issue in your scene and click Publish again.

**Q: The button disappeared or my software crashed!**
A: That's okay! We track everything. 
Manually save your progress using the normal app tools if you still can, and restart the software.
If it constantly crashes, simply navigate to `~/omnipipe/logs/` entirely outside of the software. Send the most recent `.log` file in that folder to your Technical Director. It acts like a black-box flight recorder and tells them exactly how to fix the problem instantly!
