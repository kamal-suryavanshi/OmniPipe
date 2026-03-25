from abc import ABC, abstractmethod

class BaseDCC(ABC):
    """
    Abstract Base Class for all DCCs (Maya, Nuke, Blender).
    
    This is the core architecture contract! By enforcing these methods, 
    our central PipelineAPI can blindy call 'save_as()' or 'publish()' 
    without ever needing to know if the user is in Maya or Nuke.
    
    Person B MUST implement all these methods for each host software!
    """
    
    @abstractmethod
    def get_current_file(self) -> str:
        """Returns the absolute path of the currently open DCC scene file."""
        pass
        
    @abstractmethod
    def open_file(self, filepath: str) -> bool:
        """Opens a file tightly integrated into the host software."""
        pass
        
    @abstractmethod
    def save_file(self) -> bool:
        """Saves the current file natively."""
        pass
        
    @abstractmethod
    def save_as(self, filepath: str) -> bool:
        """Saves the current scene to a new provided path."""
        pass
        
    @abstractmethod
    def publish(self, publish_path: str) -> bool:
        """
        Executes the official publishing routine. E.g. in Maya this might 
        export an Alembic cache, or in Nuke it might render a Write node sequence
        to the locked publish_path.
        """
        pass
