from lib.helpers.filesystem import resolve_path


class ProjectAlreadyExistsError(Exception):
    def __init__(self, project_dir: str):
        self.project_dir: str = project_dir
        self.message: str = "There is already a project under '{0}'.".format(resolve_path(project_dir))
        super().__init__(self.message)