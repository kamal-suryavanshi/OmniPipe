# OmniPipe Documentation

Welcome to the official documentation for **OmniPipe**, a dynamic, zero-install VFX Studio Pipeline.

To keep things perfectly simple, we have divided the documentation into four strict modules based on your role in the studio. Please select the guide that applies to you:

## 🧭 The Guides

### [1. Technical Director (TD) Guide](guides/td_guide.md)
*For Pipeline TDs and System Administrators.*
Contains the explicit, step-by-step instructions for initializing the central NAS, configuring the schema dictionaries, and deploying the workstation bundles to your studio.

### [2. QA & Tester Guide](guides/testing_guide.md)
*For QA Testers, Coordinators, and Pre-Release Checkers.*
Contains the step-by-step methodology to check NAS permissions, run the `omnipipe doctor` diagnostic, and do end-to-end publish tests in Maya and Nuke before studio deployment.

### [3. Developer Guide](guides/developer_guide.md)
*For Python Developers.*
A holistic, technical breakdown of the OmniPipe Engine. Learn how the `PipelineContext` maps against the `configs/schema.yaml`, how to write custom native Validators, and how to subclass the `DCCInterface` to bind new software like Blender or Houdini.

### [4. Artist Guide](guides/artist_guide.md)
*For the 3D Artists, Animators, and Compositors.*
A completely jargon-free, simple manual explaining how to click the "OP Save", "OP Publish", and "Load" buttons inside of your creative apps.
