# Task 9: License Validation System

Since OmniPipe will be violently compiled into a closed-source C++ executable binary via Nuitka (Task 1), Person A designed a mathematically robust cryptographic License System to absolutely prevent unauthorized outside studios from running the pipeline codebase.

## 1. Cryptographic HMAC-SHA256 Mechanics (`omnipipe/core/license.py`)
Instead of a simple boolean text file or a stupid hardcoded string that can be bypassed, the system uses true mathematical cryptography.
The `validate_license()` function reads `~/omnipipe.lic` which physically contains:
1. The target Studio Name payload.
2. An exact SHA256 hex digest signature.

It mathematically takes the Studio Name payload and hashes it locally natively in C-memory using a hidden compiled 256-bit `_SECRET_KEY`. If the locally calculated hash mathematically lines up perfectly against the signature inside the file string (using `hmac.compare_digest()` to safely prevent hash-timing attacks), the global license is validated. This makes it literally impossible for a pirate to manually type their own name into a text file and bypass the CLI system.

## 2. The Typer Global Chokepoint (`omnipipe/__main__.py`)
To prevent internal pipeline developers from accidentally forgetting to add the license check to new individual CLI commands, we strictly leveraged a global **Typer Callback**.
A Typer Callback mathematically executes globally before *any* CLI command is even routed to its function block. 

If the `hmac` cryptography algorithm natively fails, Typer inherently throws a brutal `typer.Exit(code=1)` and violently terminates the Python execution thread before the pipeline can even begin to load a module.

## 3. The Admin Generator Key (`scripts/generate_license.py`)
We physically isolated a standalone Admin script that natively leverages the master secret key to generate valid `.lic` files. This script will *never* physically be compiled into the compiled `.exe/.bin` client deliverables! It exists solely on the Lead Pipeline TD's secure internal machine.
