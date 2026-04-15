# Pipeline Developer Guide

Welcome. This document maps out the core architecture of OmniPipe for Python developers attempting to augment the pipeline, add new validators, or hook in third-party software.

OmniPipe is built entirely on generic, abstract Object-Oriented patterns to ensure high extensibility.

---

## 📋 Prerequisites
To develop and compile OmniPipe, you will need:
- Python 3.10+
- Solid understanding of OOP structure (`dataclasses`, `abc.ABC`, class inheritance).
- Access to the `configs/` folder and basic YAML parsing knowledge.

---

## Architecture Breakdown

OmniPipe's architecture guarantees that NO creative application (like Maya or Nuke) contains any actual Save/Publish logic. The DCC packages simply instantiate a `PipelineContext` and pass paths into the `PublishEngine`. This "Thin Client" architecture allows you to change how files are resolved network-wide without ever editing Maya script files.

### 1. The Context System (`omnipipe/core/context.py`)

Every action passed to the pipeline must first resolve into a unified state known as the `PipelineContext`. It requires a dataclass structure enforcing strict validation metrics.

```python
from omnipipe.core.context import PipelineContext

# Generating a context for a specific user action
ctx = PipelineContext(
    project="DEMO",
    sequence="sq010",
    shot="sh0100",
    task="anim",
    version="003",
    dcc="maya"
)

print(ctx.dcc) # Outputs 'maya'
```

### 2. The Path Resolver Engine

Instead of hardcoding save paths, you use `PathResolver` to dynamically build the absolute path string. It natively assesses what OS it is running on and returns the corresponding `Z:\` (Windows) or `/Volumes/` (Mac) drive letters securely mapped inside `configs/schema.yaml`.

```python
from omnipipe.core.context import PathResolver, PipelineContext

ctx = PipelineContext(project="DEMO", sequence="sq01", shot="sh010", task="fx", version="v002", dcc="houdini")
resolver = PathResolver()

# This calculates the physical filepath but does NOT write it to disk. 
# It utilizes the schema 'publish_file_{dcc}' template strings.
final_path = resolver.resolve("publish_file_houdini", ctx)

print(final_path) 
# /mnt/projects/DEMO/sq01/sh010/publish/houdini/fx/DEMO_sq01_sh010_fx_v002.hip
```

### 3. Core Engine Expansion (`omnipipe/core/publish.py`)

When an artist clicks "Publish", `PublishEngine.run()` triggers a cascade sequence. This is highly customizable.

**Phase A: Validators Checklist**
Validators scan files dynamically and physically abort the publish process if the boolean returns false. You must subclass `ValidatorBase`.

*Example: Adding a Naming Convention Enforcer*
```python
from omnipipe.core.publish import ValidatorBase

class StrictNamingValidator(ValidatorBase):
    def validate(self, instance) -> bool:
        forbidden_chars = [" ", "@", "!", "$"]
        for char in forbidden_chars:
            if char in instance.name:
                raise ValueError(f"CRITICAL FAULT: {char} found in node name string!")
        return True

# Register in initialization hook
engine.add_validator(StrictNamingValidator())
```

**Phase B: Extractors**
Extractors run *after* validation. They derive sub-elements (like Alembic caches, MP4 playblasts, or JSON Metadata logs). They are passive tasks that generate heavy compute files alongside the primary `.ma` or `.nk` data file.

*Example: Triggering an MP4 extraction*
```python
import os
from omnipipe.core.publish import ExtractorBase

class PlayblastExtractor(ExtractorBase):
    def extract(self, instance) -> bool:
        out_path = instance.publish_path.replace('.ma', '.mp4')
        # In a real environment, you'd trigger a maya.cmds.playblast block.
        print(f"Extracting .mp4 playblast to {out_path}")
        return True

engine.add_extractor(PlayblastExtractor())
```

### 4. Integrating a New DCC (e.g., Blender)

If you need to add pipeline buttons to a totally new software, follow this isolated factory pattern:

**Step 1:** Create `omnipipe/dcc/blender/api.py`. Implement the `DCCInterface`.

```python
from omnipipe.dcc import DCCInterface

class BlenderInterface(DCCInterface):
    """Deep pipeline binding for Blender"""
    
    def save(self) -> bool:
        import bpy
        # Code to trigger bpy.ops.wm.save_mainfile() goes here 
        return True
    
    def get_current_file(self) -> str:
        import bpy
        return bpy.data.filepath
        
    def add_menu(self):
        # UI Code mapping a physical 'OmniPipe Publish' button natively
        pass
```

**Step 2:** Register `blender` string inside the factory pattern generator found at `omnipipe/dcc/__init__.py`. 
Any application running `get_dcc("blender")` will seamlessly load your new robust class without modifying core mechanics!
