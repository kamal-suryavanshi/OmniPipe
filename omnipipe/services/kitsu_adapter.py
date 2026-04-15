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

    def get_sequence(self, project, sequence_name):
        """ Fetch a sequence entity from the Kitsu DB. """
        if not self.connected:
            raise ConnectionError("Not connected to Kitsu.")
        return gazu.shot.get_sequence_by_name(project, sequence_name)

    def get_shot(self, sequence, shot_name):
        """ Fetch a shot entity from the Kitsu DB. """
        if not self.connected:
            raise ConnectionError("Not connected to Kitsu.")
        return gazu.shot.get_shot_by_name(sequence, shot_name)

    def get_task(self, shot, task_type_name):
        """ Fetch a task for a given shot by task type name. """
        if not self.connected:
            raise ConnectionError("Not connected to Kitsu.")
        task_type = gazu.task.get_task_type_by_name(task_type_name)
        if not task_type:
            return None
        return gazu.task.get_task_by_name(shot, task_type)

    def my_tasks(self):
        """ Fetch all currently assigned tasks for the logged in user. """
        if not self.connected:
            raise ConnectionError("Not connected to Kitsu.")
        return gazu.user.all_tasks_to_do()
