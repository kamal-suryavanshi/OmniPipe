import os
import yaml
import re
from pathlib import Path
from omnipipe.core.logger import setup_logger

log = setup_logger("omnipipe.context")


class PipelineContext:
    def __init__(self, **kwargs):
        self.data = kwargs
        log.debug("PipelineContext created with keys: %s", list(kwargs.keys()))

    def get(self, key, default=None):
        return self.data.get(key, default)

    def as_dict(self):
        return self.data


class PathResolver:
    """
    Parses schema.yaml and dynamically resolves pipeline paths
    by injecting context variables or referring to other YAML templates.
    """
    def __init__(self, schema_path: str = None):
        if not schema_path:
            root_dir = Path(__file__).parent.parent.parent
            schema_path = root_dir / "configs" / "schema.yaml"
        self.schema_path = Path(schema_path)
        log.debug("PathResolver initialising from schema: %s", self.schema_path)
        self.schema = self._load_schema()

    def _load_schema(self) -> dict:
        if not self.schema_path.exists():
            log.error("Schema YAML not found at: %s", self.schema_path)
            raise FileNotFoundError(f"Schema not found at {self.schema_path}")
        with open(self.schema_path, "r") as f:
            data = yaml.safe_load(f)
        log.info("Schema loaded successfully: %s", self.schema_path.name)
        return data

    def resolve(self, template_name: str, context: PipelineContext,
                check_exists: bool = False) -> str:
        templates = self.schema.get("templates", {})
        if template_name not in templates:
            log.error("Template '%s' not found in schema. Available: %s",
                      template_name, list(templates.keys()))
            raise ValueError(f"Template '{template_name}' not found in schema.")

        raw_env = context.as_dict().copy()
        raw_env["STUDIO_ROOT"] = os.getenv("STUDIO_ROOT", "/tmp/studio")

        for k, v in self.schema.items():
            if isinstance(v, str):
                templates[k] = v

        resolved = self._resolve_recursive(templates[template_name], templates, raw_env)
        log.debug("Resolved '%s' → %s", template_name, resolved)

        if check_exists:
            import os as _os
            if not _os.path.exists(resolved):
                log.warning(
                    "Resolved path does NOT exist on disk: '%s' "
                    "(template='%s'). File may not have been written yet.",
                    resolved, template_name
                )
            else:
                log.debug("Existence check passed for: %s", resolved)

        return resolved

    def _resolve_recursive(self, template_str: str, templates: dict, env: dict) -> str:
        matches = re.findall(r"\{([^}]+)\}", template_str)
        for match in matches:
            if match in env:
                val = str(env[match])
            elif match in templates:
                val = self._resolve_recursive(templates[match], templates, env)
            else:
                log.error("Missing context variable or template key: '%s'", match)
                raise KeyError(f"Missing context variable or template for '{match}'")
            template_str = template_str.replace(f"{{{match}}}", val)

        os_path = Path(template_str)
        return str(os_path).replace("\\", "/")
