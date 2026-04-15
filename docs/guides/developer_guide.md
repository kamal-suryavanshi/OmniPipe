# Pipeline Developer Guide

Welcome. This document maps out the core architecture of OmniPipe for Python developers. OmniPipe is built entirely on generic, abstract Object-Oriented patterns to ensure high extensibility.

## 📋 Prerequisites
To develop and compile OmniPipe, you will need:
- Python 3.10+
- Familiarity with Object-Oriented Python (`dataclasses`, `abc.ABC`, `typing`).
- An understanding of the `configs/schema.yaml` definition file.

---

## 1. The Context System

The backbone of OmniPipe is the `PipelineContext` dataclass located in `omnipipe/core/context.py`. Every action passed to the pipeline must first resolve into a Context.
```python
from omnipipe.core.context import PipelineContext

ctx = PipelineContext(
    project="DEMO",
    sequence="sq010",
    shot="sh0100",
    task="anim",
    version="003",
    dcc="maya"
)
```

## 2. The Path Resolver Engine

Instead of hardcoding save paths inside pipeline scripts, the `PathResolver` dynamically generates physical absolute paths based on the `configs/schema.yaml` template.
```python
from omnipipe.core.context import PathResolver

resolver = PathResolver()
final_path = resolver.resolve("publish_file_maya", ctx)
# Output Example: /mnt/projects/DEMO/sq010/sh0100/publish/maya/anim/DEMO_sq010_sh0100_anim_v003.ma
```

## 3. The Publish Engine

The `PublishEngine` (`omnipipe/core/publish.py`) acts as a linear execution pipeline for files entering the production tracking state.

### Phase 1: Validators
Validators scan files dynamically and physically abort the publish process if criteria aren't met.
**Example Validator:**
```python
from omnipipe.core.publish import ValidatorBase

class CheckSpaceValidator(ValidatorBase):
    def validate(self, instance) -> bool:
        if " " in instance.name:
            raise ValueError("Spaces are banned in filenames!")
        return True
```

### Phase 2: Extractors
Extractors derive sub-elements (like Alembic generic caches, Playblasts, or JSON Metadata sidecar payload drops).
```python
from omnipipe.core.publish import ExtractorBase

class PlayblastExtractor(ExtractorBase):
    def extract(self, instance) -> bool:
        print(f"Extracting .mp4 from {instance.source_path}")
        return True
```

## 4. Integrating a New DCC

To write wrappers for an entirely new software (e.g. Blender or Houdini):
1. Create a folder: `omnipipe/dcc/blender/`
2. Create an `api.py` implementing the abstract `DCCInterface` (from `omnipipe/dcc/__init__.py`).
```python
from omnipipe.dcc import DCCInterface

class BlenderInterface(DCCInterface):
    def save(self) -> bool:
        import bpy
        bpy.ops.wm.save_mainfile()
        return True
    
    def get_current_file(self) -> str:
        import bpy
        return bpy.data.filepath
```
3. Hook your `startup.py` scripts natively into the software's boot architecture!
