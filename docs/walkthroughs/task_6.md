# Task 6: Extractors

After a file reliably survives the Gatekeepers (Task 5) and mathematically increments its version logically (Task 4), the pipeline must actually automatically extract the required outputs (like MP4 Playblasts or EXR frames) for the Production Managers to review.

## 1. The Extractor Base Class (`omnipipe/core/extractors.py`)
Person A built `BaseExtractor` as a pure plugin template, identical to Validators. These extractor classes are designed to be centrally plugged into `PublishEngine.run()`.

### Built-in Standard Extractors
- **EXRSequenceExtractor**: Directly natively interfaces with Maya V-Ray or Nuke Write nodes to physically render and copy `.exr` frames natively to the active `PublishInstance` output folder. For our development environment, it mathematically mocks this by writing 3 dummy text-based `.exr` files to strictly prove the OS permissions and path structures resolve securely on the file server.
- **PlayblastExtractor**: Hooks cleanly into the Maya Viewport API to aggressively rip a fast `.mp4` video. For our setup, it writes a mock string video file to verify the exact output destination correctly string-replaces `.ma` with `.mp4`.

## 2. PublishEngine Integration
The `PublishEngine` natively executes these Extractors strictly *after* the `is_valid` flag is marked True mathematically by the Validators in Phase 1. If a file is fatally broken, it will purposefully never trigger a heavy automated EXR render extraction queue.
