# OmniPipe Master Test Plan

This document outlines the strict quality-assurance testing checklist that must be physically performed by the Lead TD at the end of the entire development lifecycle. Each test directly corresponds to the official Excel Tracker Roadmap.

## Pipeline Core Validation (Person A)

- [ ] **Task 1: Repo Setup (Zero-Install)**
  Run `python -m omnipipe login` on a fresh Windows, Mac, and Linux machine with zero `pip` installations to verify the bundled generic dependencies boot securely.
  
- [ ] **Task 2: Context System**
  Pass `--sequence seq01 --shot sh010` into `python -m omnipipe context` and visually verify the exact drive letters resolve successfully based purely on `schema.yaml`.

- [ ] **Task 3: Path Manager**
  Verify the Typer CLI output mathematically generated the exact physical drive URLs and extension templates.

- [ ] **Task 4: Publish Design (Versioning)**
  Drop three files (`v001`, `v002`, `v008`) into a dummy terminal directory and run `versioning.py` against them. Confirm `get_next_available_path()` intelligently jumps to `v009`.

- [ ] **Task 5: Validators**
  Submit a purposefully broken `PublishInstance` containing a forbidden space string and confirm the `NamingConventionValidator` brutally blocks the sequence loop.

- [ ] **Task 6: Extractors**
  Confirm a valid `PublishInstance` successfully dumps a dummy MP4 Playblast alongside the `.ma` file dynamically during Phase 2 of the `PublishEngine`.

- [ ] **Task 7: Metadata Tracking**
  After a simulated publish, navigate to the output folder and confirm the payload `{filename}.json` file was autonomously created and correctly securely recorded the local OS user signature.

- [ ] **Task 8: Dependency Tracking**
  Set `enable_dependency_tracking: true` globally inside `configs/schema.yaml`. Publish a dummy file natively and confirm the resulting JSON automatically injects the `dependencies` tracker array cleanly without crashing.
  
- [ ] **Task 9: License System**
  Delete the physical `~/omnipipe.lic` key file and attempt to natively run `python -m omnipipe context`. Confirm the Typer CLI violently terminates execution with a `FATAL LICENSE ERROR` before loading the pipeline context. Then natively execute `python scripts/generate_license.py "OmniPipe Studio"` and confirm the cryptographic block seamlessly lifts.

- [ ] **Task 10: Error Handling**
  Open `omnipipe/__main__.py` and physically inject a runtime error natively (e.g., `1/0`) inside any initialized command. Run the CLI mechanically. Navigate straight to `~/omnipipe/logs/pipeline.log` to visually verify the exact detailed programmatic stack trace was fully mathematically captured!

## DCC Headless Mechanics (Person B)

- [ ] **Maya Dev-Mode:** Run `python -m omnipipe test-dcc maya` natively outside of the software and confirm the fallback `[MAYA DEV MODE]` logic does not throw tracebacks.
- [ ] **Nuke Dev-Mode:** Run `python -m omnipipe test-dcc nuke` natively outside of the software and confirm the Nuke integrations bypass effectively.
- [ ] **Native Soft-Hook:** Import `omnipipe.dcc.maya.api` locally inside Autodesk Maya's internal python script editor and execute `publish()`. Confirm the `.ma` effectively writes cleanly to the disk without user interface involvement.

## Production Compilation (Nuitka C++)
- [ ] **Windows EXE & Mac Binary:** Run `python build.py`. Launch the local `.exe` and `.bin` natively without the system requiring a single python pip install.
