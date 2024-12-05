from argparse import Namespace

from lib.builder.state import ProjectBuilderState
from lib.config.config import ProjectConfig


class ProjectBuilder:
    def __init__(self, config: ProjectConfig, arguments: Namespace):
        self.config: ProjectConfig = config
        self.arguments: Namespace = arguments
        self.state: ProjectBuilderState = ProjectBuilderState.from_empty(arguments=arguments, config=self.config)

    def build(self) -> ProjectBuilderState:
        self._build_charts()
        self._build_manifests()
        return self.state

    def _build_charts(self):
        for chart in self.config.get_helm_releases():
            self.state.set_chart(chart)

    def _build_manifests(self):
        for manifest in self.config.get_kubectl_manifests():
            self.state.set_manifest(manifest)
