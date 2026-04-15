# Artist Guide

Welcome to OmniPipe! This guide is written specifically for 3D Artists, Compositors, and Animators.

OmniPipe is designed to be completely invisible until you need it. You don't have to navigate messy network folders or worry about naming your files correctly. OmniPipe handles all the boring data management so you can focus strictly on the art!

---

## 📋 Prerequisites
Before you begin your day:
1. Ensure your studio TD has provided you with your `omnipipe.lic` file.
2. Wait for the `Install Complete ✅` message from your local workstation script (your coordinator will launch this for you).
3. Ensure you are connected to the central Studio Server (e.g. `Z:\` drive).

---

## What Does OmniPipe Do?
When you are working in Maya, Nuke, or Silhouette, OmniPipe adds three magical buttons to your interface: **Save**, **Publish**, and **Load**.

### 1. OmniPipe Save (OP Save)
**What it does:** Saves your current work file (often called your `work` directory).
- If it is your very first time clicking save on a new file, it will ask you what Shot and Task you are doing, and then physically put the file in the exact right network folder.
- If you have already saved before, it will just automatically bump up your version number! (e.g. from `_v034` to `_v035`).

### 2. OmniPipe Publish (OP Publish)
**What it does:** Freezes an "approved" version of your work and ships it down the pipeline.
- Work files (`OP Save`) are messy and can break. Publishes (`OP Publish`) are permanent snapshots.
- When you click Publish, OmniPipe scans your scene for messy geometry names or dangerous links, takes a snapshot, and copies it to a locked `publish/` folder where Lighters and Compositors can safely grab it.

### 3. OmniPipe Load (OP Load / Load Latest)
**What it does:** Grabs the absolute latest published file from an upstream department.
- If you are a Compositor in Nuke and need the latest Animation render, clicking Load Latest will instantly drop the newest Read node into your script, guaranteed to be the version the Director just approved.

---

## FAQ

**Q: Where did my file just go?**
A: You can always look at the top of your Maya/Nuke window. OmniPipe automatically names your file based on the Studio naming convention (e.g. `DEMO_sq010_sh0100_anim_v001.ma`).

**Q: I got a red "VALIDATION ERROR" when publishing! What do I do?**
A: Read the pop-up carefully. OmniPipe stops you from publishing if you left a space in a node name, or forgot to link a texture. Fix the issue in your scene and click Publish again.

**Q: The button disappeared or my software crashed!**
A: Save your progress manually if you can, restart the app, and if it's still broken, message your Technical Director. They have automated logs they can check to fix it immediately!
