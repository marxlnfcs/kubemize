from lib.helpers.filesystem import resolve_path


class ProjectNotFoundError(Exception):
    def __init__(self, project_file: str, project_dir: str):
        self.project_file: str = project_file
        self.project_dir: str = project_dir
        self.message: str = "The directory '{0}' is not a valid project dir. Please check path or create a new project with 'kubemize new'.".format(resolve_path(project_file, cwd=project_dir))
        super().__init__(self.message)