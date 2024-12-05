import argparse

from lib.project import Project


class Commander(argparse.ArgumentParser):
    def __init__(self, version: str = None, **kwargs):
        super().__init__(**kwargs)
        self.add_argument('--version', action='version', version=f"%(prog)s {version}")

    def get_subparser(self):
        if not hasattr(self, "__sub_parser__"):
            self.__setattr__("__sub_parser__", self.add_subparsers(
                dest="command",
                required=True,
            ))
        return self.__getattribute__("__sub_parser__")


class CommanderCommand:
    def __init__(self, name: str, description: str):
        self.name: str = name
        self.description: str = description

    def commands(self, commander: Commander):
        pass


class CommanderCommandForProject(CommanderCommand):
    def run(self, project: Project):
        pass


class CommanderCommandStandalone(CommanderCommand):
    def run(self, arguments: argparse.Namespace):
        pass
