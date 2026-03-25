import os
import yaml
import re
from pathlib import Path

class PipelineContext:
    def __init__(self, **kwargs):
        self.data = kwargs
        
    def get(self, key, default=None):
        return self.data.get(key, default)
        
    def as_dict(self):
        return self.data

class PathResolver:
    """
    Parses the schema.yaml and dynamically resolves pipeline paths
    by injecting context variables or referring to other YAML templates.
    """
    def __init__(self, schema_path: str = None):
        if not schema_path:
            # Default to configs/schema.yaml located at project root
            root_dir = Path(__file__).parent.parent.parent
            schema_path = root_dir / "configs" / "schema.yaml"
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()

    def _load_schema(self):
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema not found at {self.schema_path}")
        with open(self.schema_path, "r") as f:
            return yaml.safe_load(f)

    def resolve(self, template_name: str, context: PipelineContext) -> str:
        templates = self.schema.get("templates", {})
        if template_name not in templates:
            raise ValueError(f"Template '{template_name}' not found in schema.")
            
        raw_env = context.as_dict().copy()
        raw_env["STUDIO_ROOT"] = os.getenv("STUDIO_ROOT", "/tmp/studio")
        
        # Inject base keys from the document root into the flat templates dict
        for k, v in self.schema.items():
            if isinstance(v, str):
                templates[k] = v
                
        return self._resolve_recursive(templates[template_name], templates, raw_env)

    def _resolve_recursive(self, template_str: str, templates: dict, env: dict) -> str:
        # Recursively find all {var} patterns in the string
        matches = re.findall(r"\{([^}]+)\}", template_str)
        for match in matches:
            if match in env:
                # Variable was directly provided in the context or environment
                val = str(env[match])
            elif match in templates:
                # Variable is actually a reference to another template snippet
                val = self._resolve_recursive(templates[match], templates, env)
            else:
                raise KeyError(f"Missing context variable or template for '{match}'")
                
            template_str = template_str.replace(f"{{{match}}}", val)
            
        # Normalize slashes safely for OS
        os_path = Path(template_str)
        return str(os_path).replace("\\", "/") # Enforce forward slash in generic system until mapped
