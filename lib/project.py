from argparse import Namespace

from lib.builder.builder import ProjectBuilder
from lib.builder.state import ProjectBuilderState
from lib.config.config import ProjectConfig
from lib.helpers.filesystem import resolve_path, file_exists, dir_exists
from lib.helpers.helm import Helm
from lib.helpers.kubectl import Kubectl
from lib.hooks_runner import ProjectHooksRunner
from lib.plan.plan import ProjectPlan
from lib.provisioner import ProjectProvisioner
from lib.state.state import ProjectState


class Project:
    def __init__(self, arguments: Namespace):
        self.config: ProjectConfig = ProjectConfig(arguments.project, arguments.config, arguments)
        self.arguments: Namespace = arguments
        self.state_current: ProjectState = ProjectState.from_file(arguments.state, cwd=arguments.project, arguments=self.arguments, config=self.config)
        self.state_new: ProjectState = ProjectState.from_empty(arguments=arguments, config=self.config)

    def get_project_dir(self) -> str:
        return resolve_path(self.arguments.project)

    def get_project_file(self) -> str:
        return resolve_path(self.arguments.config, cwd=self.get_project_dir())

    def get_project_state_file(self) -> str:
        return resolve_path(self.arguments.state, cwd=self.get_project_dir())

    def project_exists(self) -> bool:
        return dir_exists(self.get_project_dir())

    def project_state_exists(self) -> bool:
        return file_exists(self.get_project_state_file())

    def get_current_state(self) -> ProjectState:
        return self.state_current

    def get_new_state(self) -> ProjectState:
        return self.state_new

    def create_plan(self, state: ProjectState or ProjectBuilderState = None) -> ProjectPlan:
        return ProjectPlan(config=self.config, state_current=self.get_current_state(), state_new=state if state is not None else self.build())

    def create_provisioner(self) -> ProjectProvisioner:
        return ProjectProvisioner(project=self, state=self.get_new_state())

    def get_hooks_runner(self) -> ProjectHooksRunner:
        return ProjectHooksRunner(project=self)

    def get_helm(self) -> Helm:
        return Helm(self.config.get_helm_executable())

    def get_kubectl(self) -> Kubectl:
        return Kubectl(self.config.get_kubectl_executable())

    def build(self) -> ProjectBuilderState:
        return ProjectBuilder(self.config, arguments=self.arguments).build()