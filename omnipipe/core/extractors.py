import os
import shutil
from abc import ABC, abstractmethod
from omnipipe.core.publish import PublishInstance

class BaseExtractor(ABC):
    """
    Abstract interface for all Publishing Extractors (Output generators).
    """
    @property
    def name(self) -> str:
        return self.__class__.__name__
        
    @abstractmethod
    def extract(self, instance: PublishInstance) -> bool:
        """
        Logic to physically rip or render outputs from the native DCC.
        """
        pass

class EXRSequenceExtractor(BaseExtractor):
    """
    Mocks exporting an EXR sequence from the render engine.
    In real production, this bridges dynamically to Nuke's Write node or Maya's V-Ray.
    """
    def extract(self, instance: PublishInstance) -> bool:
        # Mock logic: Create dummy frames cleanly alongside the publish
        output_dir = os.path.dirname(instance.publish_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Simulate generating 3 frames
        for i in range(1, 4):
            frame_path = os.path.join(output_dir, f"frame_{i:04d}.exr")
            with open(frame_path, "w") as f:
                f.write("DUMMY_EXR_DATA_FRAME")
                
        print(f"  [EXTRACTOR] Successfully mocked EXR extraction to: {output_dir}")
        return True

class PlayblastExtractor(BaseExtractor):
    """
    Mocks natively exporting an MP4 Playblast from the Maya viewport.
    """
    def extract(self, instance: PublishInstance) -> bool:
        pb_path = instance.publish_path.replace(".ma", ".mp4")
        with open(pb_path, "w") as f:
            f.write("DUMMY_MP4_VIDEO_DATA")
            
        print(f"  [EXTRACTOR] Successfully mocked Playblast extraction to: {pb_path}")
        return True
