import os
import gazu

class KitsuAdapter:
    """
    An adapter for interacting with Kitsu's backend (Zou).
    Uses the official gazu python client.
    """
    def __init__(self):
        self.host = os.getenv("KITSU_HOST", "http://localhost/api")
        self.login = os.getenv("KITSU_LOGIN", "admin@example.com")
        self.password = os.getenv("KITSU_PWD", "default_password")
        self.connected = False

    def connect(self):
        """
        Attempts to authenticate with the Kitsu backend.
        """
        gazu.client.set_host(self.host)
        try:
            gazu.log_in(self.login, self.password)
            self.connected = True
            return True
        except Exception as e:
            # We catch generic exceptions here if the Zou server is not running locally.
            self.connected = False
            return False

    def get_project(self, project_name):
        """ Fetch a project entity from the Kitsu DB. """
        if not self.connected:
            raise ConnectionError("Not connected to Kitsu.")
        return gazu.project.get_project_by_name(project_name)
