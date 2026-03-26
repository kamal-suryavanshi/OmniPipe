# Task 9: License Validation System

Since OmniPipe will be violently compiled into a closed-source C++ executable binary via Nuitka (Task 1), Person A designed a mathematically robust cryptographic License System to absolutely prevent unauthorized outside studios from running the pipeline codebase.

## 1. Cryptographic HMAC-SHA256 Mechanics (`omnipipe/core/license.py`)
Instead of a simple boolean text file or a stupid hardcoded string that can be bypassed, the system uses true mathematical cryptography.
The `validate_license()` function reads `~/omnipipe.lic` which physically contains:
1. The target Studio Name payload.
2. An exact SHA256 hex digest signature.

It mathematically takes the Studio Name payload and hashes it locally natively in C-memory using a hidden compiled 256-bit `_SECRET_KEY`. If the locally calculated hash mathematically lines up perfectly against the signature inside the file string (using `hmac.compare_digest()` to safely prevent hash-timing attacks), the global license is validated. This makes it literally impossible for a pirate to manually type their own name into a text file and bypass the CLI system.

## 2. The DCC & Engine Choke Points (`omnipipe/dcc/` & `validators.py`)
To perfectly balance security without blinding the artists, we shifted the License Cryptography injection AWAY from the global CLI block and dynamically injected it mechanically into two physical fatal choke points:

1.  **DCC Physical Writes (`maya/api.py`, `nuke/api.py`)**: Before an internal architectural DCC can natively trigger `save_file()` or `save_as()`, it blindly executes `validate_license()`. If validation fails, the save logic is instantly aggressively blocked, physically preventing unlicensed project data from touching the hard drive.
2.  **PublishEngine Gatekeeper (`core/validators.py`)**: We logically constructed `LicenseValidator()` as a Task 5 security gatekeeper. When `PublishEngine.run()` triggers, it seamlessly mathematically forces an internal cryptography check, strictly refusing secure metadata extraction or pipeline file synchronization unless the signature perfectly matches.

This exact architectural native pivot cleanly efficiently allows local artists to safely use generic pipeline query tools natively (like `omnipipe context`) without a license key, but freeze structurally all permanent extraction and generation functions if DRM fails!

## 3. The Admin Generator Key (`scripts/generate_license.py`)
We physically isolated a standalone Admin script that natively leverages the master secret key to generate valid `.lic` files. This script will *never* physically be compiled into the compiled `.exe/.bin` client deliverables! It exists solely on the Lead Pipeline TD's secure internal machine.
