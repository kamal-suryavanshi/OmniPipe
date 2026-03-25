from omnipipe.core.context import PipelineContext, PathResolver
from omnipipe.services.kitsu_adapter import KitsuAdapter

class PipelineAPI:
    """
    The Central Access Hub for OmniPipe.
    All CLI and DCC tools should interface with this class instead 
    of calling submodules independently.
    """
    def __init__(self):
        self.resolver = PathResolver()
        self.asset_manager = KitsuAdapter()
        
    def login(self):
        """ Wrapper for Asset Manager authentication. """
        return self.asset_manager.connect()
        
    def build_context(self, project, sequence, shot, task, version="001", dcc="maya"):
        """
        Constructs a PipelineContext. In the future, this will query 
        the asset manager (Kitsu) to validate that the shot actually exists.
        """
        return PipelineContext(
            project=project,
            sequence=sequence,
            shot=shot,
            task=task,
            version=version,
            dcc=dcc
        )
