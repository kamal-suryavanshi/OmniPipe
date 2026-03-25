# Day 3: Pipeline Core Services

## Objectives
- Integrate the official Kitsu API (`gazu`).
- Abstract the Context System and Asset Manager into a unified `PipelineAPI`.
- Provide CLI users a way to authenticate against the server.

## Implementations
- Created `KitsuAdapter` in `omnipipe/services/kitsu_adapter.py`. It reads from `.env` and issues live connection requests to Kitsu databases (like Zou).
- Created `PipelineAPI` in `omnipipe/core/pipeline.py` which unifies the Path logic and Asset Data fetching into a single unified endpoint for DCCs.
- Updated the CLI to include the `omnipipe login` command.

## Verification
Users can now run:
```bash
poetry run omnipipe login
```
Which tests the connection handshake. If Zou is running locally on port 80, it returns `Success! Connected to Asset Manager.`, otherwise it gracefully handles errors letting the user know to correct `.env`.
