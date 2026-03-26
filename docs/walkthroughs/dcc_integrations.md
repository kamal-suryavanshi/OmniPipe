# Day 4: Headless DCC Integrations

Person B is responsible for integrating Autodesk Maya and Foundry Nuke into the OmniPipe ecosystem. 
Because Studio APIs must blindly trust that DCCs execute the same logic safely, we created a strict interface contract.

## 1. The Architectural Contract (`omnipipe/dcc/base.py`)
Person A constructed the `BaseDCC` Abstract Base Class. It mandates that any software claiming to be an OmniPipe-certified DCC **must** implement these exact functions:
- `get_current_file()`
- `open_file()`
- `save_file()`
- `save_as()`
- `publish()`

## 2. Platform Agnostic Loaders
We built `MayaDCC` and `NukeDCC` in `omnipipe/dcc/maya/api.py` and `omnipipe/dcc/nuke/api.py`.
Crucially, these python modules wrap the native software packages (`import maya.cmds` or `import nuke`) in `try/except ImportError` blocks.

**Why?** This guarantees that a Developer building the web backend or CLI on a laptop that *does not* have Maya installed can still safely run and test the python code without the pipeline crashing from import errors. The loader automatically degrades into `[DEV MODE]` and simulates the save functions securely via terminal logs.

## 3. How to Test It Instantly
We added a built-in testing suite to the Typer CLI in the root `omnipipe/__main__.py`. Any developer can verify the hooks are intact by running the testing command:

**Test Maya:**
```bash
python -m omnipipe test-dcc maya
```

**Test Nuke:**
```bash
python -m omnipipe test-dcc nuke
```
The dummy output confirms the BaseDCC interface handlers execute seamlessly natively inside the terminal without crashing!
