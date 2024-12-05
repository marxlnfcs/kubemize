from argparse import Namespace

from lib.helpers.commander import Commander, CommanderCommandStandalone
from lib.project_creator import ProjectCreator


class CommandNew(CommanderCommandStandalone):
    def __init__(self):
        super().__init__(
            name="new",
            description="Creates a new project current directory or in the directory that was defined with the argument '--project=/path/to/project_dir'."
        )

    def commands(self, commander: Commander):
        pass

    def run(self, arguments: Namespace):
        ProjectCreator(arguments.project, arguments.config).create()