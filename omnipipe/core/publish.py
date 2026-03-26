from typing import Dict, Any, List
from dataclasses import dataclass, field
from omnipipe.core.context import PipelineContext

@dataclass
class PublishInstance:
    """
    Represents a single immutable asset or file hitting the publish pipeline.
    This enforces strict standardization of metadata so artists can't save 
    random messy files to the server.
    """
    name: str  # e.g. "character_geo" or "main_camera"
    context: PipelineContext
    source_path: str
    publish_path: str = ""
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Internal pipeline state tracking
    is_valid: bool = False
    is_extracted: bool = False

class PublishEngine:
    """
    The central orchestrator. Person A built this engine to blindly run 
    Validators (Task 5) and Extractors (Task 6) across any PublishInstance.
    """
    def __init__(self):
        self.instances: List[PublishInstance] = []
        self.validators = []  # Will be populated in Task 5
        self.extractors = []  # Will be populated in Task 6
        
    def add_instance(self, instance: PublishInstance):
        self.instances.append(instance)
        
    def register_validator(self, validator):
        """Plugin injection for Task 5 Gatekeepers"""
        self.validators.append(validator)

    def register_extractor(self, extractor):
        """Plugin injection for Task 6 Outputs"""
        self.extractors.append(extractor)

    def run(self) -> bool:
        """
        Executes the full pipeline strictness lifecycle:
        1. Validations -> 2. Extractions -> 3. Metadata tracking
        """
        print(f"\n[OmniPipe] Starting Publish Engine across {len(self.instances)} instances...")
        
        # Phase 1: Validations (Task 5)
        for instance in self.instances:
            print(f"  -> Validating {instance.name}...")
            for validator in self.validators:
                try:
                    validator.validate(instance)
                except Exception as e:
                    print(f"  [❌ FAILED] Validation Error on {instance.name}: {e}")
                    return False
            instance.is_valid = True
            print(f"  [✅ PASSED] Cleared all {len(self.validators)} security validators.")
            
        # Phase 2: Extractions (Task 6)
        if instance.is_valid:
            for extractor in self.extractors:
                print(f"  -> Extracting Output: {extractor.name}...")
                extractor.extract(instance)
            instance.is_extracted = True
            
        return True
