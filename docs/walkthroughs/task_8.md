# Task 8: Dependency Tracking

Not all CG studio clients require strict recursive dependency mapping, so Person A smartly incorporated Dependency Tracking as a **flexible toggle**.

## 1. The Global Client Toggle (`schema.yaml`)
By adding `enable_dependency_tracking: false` to the YAML config, the backend avoids heavy parsing operations. If a Lead TD flips it to `true`, the `PublishEngine` fundamentally alters its execution behaviors online.

## 2. Tracking Engine (`omnipipe/core/dependencies.py`)
If enabled, Phase 2.5 occurs cleanly after Extractions but directly *before* the Metadata JSON is committed to disk.
The script parses the exact bytes inside the DCC Scene. If it detects a Maya Reference pointing to an upstream Character Rig, it caches that physical path.

## 3. Metadata Injection
The dynamically found paths are injected centrally straight into the `PublishInstance` `metadata` dictionary. Phase 3 (The Task 7 Extractor) passively processes this new data, dynamically writing an array of `["dependencies"]` into the final `{filename}.json` without requiring any code architecture changes.
