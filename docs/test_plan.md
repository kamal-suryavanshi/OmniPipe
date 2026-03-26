# OmniPipe Master Test Plan

This document outlines the strict quality-assurance testing checklist that must be physically performed by the Lead TD at the end of the entire development lifecycle, before deploying the pipeline into commercial production.

## Phase 1: Core Architecture Validations
- [ ] **1. Zero-Install Execution:** Run `python -m omnipipe login` on a fresh Windows, Mac, and Linux machine with zero `pip` installations to verify vendorizing.
- [ ] **2. Context Pathing:** Pass `--sequence seq01 --shot sh010` into `python -m omnipipe context` and visually verify the drive letters resolve correctly on a mixed OS environment.
- [ ] **3. Kitsu Connectivity:** Successfully poll a dummy active project from the central Zou DB server.

## Phase 2: DCC Headless Mechanics
- [ ] **1. Maya Dev-Mode:** Run `python -m omnipipe test-dcc maya` outside of the software and confirm the dummy `[MAYA DEV MODE]` save logic does not throw Python tracebacks.
- [ ] **2. Nuke Dev-Mode:** Run `python -m omnipipe test-dcc nuke` outside of the software and confirm the fallback works.
- [ ] **3. Native Soft-Hook:** Import `omnipipe.dcc.maya.api` natively inside Autodesk Maya's script editor and blindly run `publish()`. Confirm the `.ma` file physically writes to the `/publish/` disk location.

## Phase 3: Publishing Engine
- [ ] **1. Version Traversal (Task 4):** Drop three files (`v001`, `v002`, `v008`) into a temp directory and run the `versioning.py` engine against them. Confirm `get_next_available_path` mathematically jumps to `v009`.
- [ ] **2. Validation Gatekeeping (Task 5):** Submit a purposefully broken `PublishInstance` containing invalid uppercase naming and confirm the `Validator` completely blocks the publish.
- [ ] **3. Extraction Automation (Task 6):** Confirm a valid `PublishInstance` correctly generates a dummy Playblast alongside the native save.

## Phase 4: Production Compilation (Nuitka C++)
- [ ] **1. Windows EXE:** Run `python build.py` on a Windows machine. Double-click `omnipipe.bat` natively and confirm instant startup.
- [ ] **2. Mac Binary:** Run `python build.py` on macOS. Run `./omnipipe.sh` natively and confirm startup.
