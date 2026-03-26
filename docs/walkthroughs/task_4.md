# Task 4: Publish Design & Versioning

As the Lead Pipeline Architect, Person A built the strict mathematical structures that control exactly how artist data hits the server.

## 1. The Versioning Engine (`omnipipe/core/versioning.py`)
To permanently prevent artists from accidentally erasing or overwriting someone else's work, the central pipeline calculates file versions dynamically using Regular Expressions.

When an artist clicks publish, the network solver recursively scans the entire Sequence directory. If it finds `char_v001.ma`, `char_v002.ma`, and `char_v008.ma`, the math engine bypasses the missing versions and securely jumps straight to `char_v009.ma`.

## 2. The Publish Orchestrator (`omnipipe/core/publish.py`)
We built a robust, type-checked `PublishInstance` memory class. This forces all software globally (Maya, Nuke, Blender) to package their active scene data into an identically shaped dictionary containing:
- The Target Context String (Show/Sequence/Shot)
- The Source Path (Where it came from)
- The Published Path (Where it mathematically needs to go)
- Custom Extracted Metadata

When an artist clicks "Publish", `PublishEngine.run()` safely catches that `PublishInstance` slot and begins sequentially executing Validators and Extractors dynamically.
