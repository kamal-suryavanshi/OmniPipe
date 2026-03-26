# Task 5: Validators (Gatekeepers)

To ensure no broken or misnamed files ever reach the global studio server, Person A injected strict Python Gatekeepers into the `PublishEngine`.

## 1. The Validation Interface (`omnipipe/core/validators.py`)
Validators are small, lightweight Python classes that act as plugins. Every validator inherits from the `BaseValidator` template. 
If an artist's scene file violates a studio rule, the validator intentionally raises a `ValueError` which instantly aborts the Publish Engine from saving the file to the network.

### Built-in Standard Gatekeepers
- **FileExistsValidator**: Before doing anything, the pipeline checks to ensure Maya/Nuke actually successfully wrote the file to disk locally. If it crashed and didn't write the file, the publisher aborts.
- **NamingConventionValidator**: A brutal Gatekeeper that checks the filename format. Spaces (` `) or special characters (like `%`, `$`) will corrupt Linux render-farm packets, so this validator blocks any artist from publishing scenes containing them.

## 2. PublishEngine Integration (`omnipipe/core/publish.py`)
The `PublishEngine.run()` method has been upgraded to loop sequentially over all registered validator plugins and aggressively test the `PublishInstance` against them. If the file survives all checks, it is mathematically marked `is_valid = True` and proceeds to Phase 2 (Extraction).
