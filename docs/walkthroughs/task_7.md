# Task 7: Metadata Tracking

Once a digital file logically increments its math version (Task 4), survives security Validations (Task 5), and dynamically Generates Outputs (Task 6), Person A designed a centralized data system to cement it perfectly on the server so other pipeline tools (like the Workfile Manager UI) can instantly read it.

## 1. The Global Metadata Standard (`omnipipe/core/metadata.py`)
Person A built `generate_publish_metadata(instance: PublishInstance)`. This rigid Python function generates an identical `{filename}.json` payload immediately alongside the physically published `.ma` or `.nk` file on the hard drive.

### The JSON Payload
No matter if a 3D artist uses Maya, Nuke, Blender, or Houdini, the payload logic uniformly forces the dictionary to contain:
- The exact OS user signature (`getpass.getuser()`)
- The precise Epoch timestamp and human-readable UTC verification date
- The physically approved Source Path and Published Path
- The intelligently resolved `PipelineContext` tags (`Sequence`, `Shot`, `Task`)

## 2. PublishEngine Integration
The native `PublishEngine.run()` method securely executes this code exclusively as **Phase 3**. It securely prevents any metadata from writing if the validation engine aborted the file dynamically in Phase 1.
