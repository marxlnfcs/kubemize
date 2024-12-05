import typing
from argparse import Namespace

from schema import SchemaError

from lib.config.schemes.helm_release import ProjectConfigHelmRelease
from lib.config.schemes.kubectl_manifest import ProjectConfigKubectlManifest
from lib.helpers.filesystem import file_exists
from lib.helpers.jsons import JSON
from lib.state.schemes.chart import ProjectStateChart
from lib.state.schemes.manifest import ProjectStateManifest
from lib.state.validator import ProjectStateValidator

if typing.TYPE_CHECKING:
    from lib.config.config import ProjectConfig

class ProjectState:
    def __init__(self, state: dict, arguments: Namespace, config: "ProjectConfig"):
        self.state: dict = state
        self.arguments: Namespace = arguments
        self.config: "ProjectConfig" = config
        ProjectStateValidator().validate(self.state)
        self._build()

    def _build(self):
        for path in self.state["charts"]:
            self.state["charts"][path] = ProjectStateChart(self.state["charts"][path], config=self.config)
        for path in self.state["manifests"]:
            self.state["manifests"][path] = ProjectStateManifest(self.state["manifests"][path], config=self.config)

    @staticmethod
    def from_file(file: str, arguments: Namespace, config, cwd: str = None):
        try:
            if file_exists(file, cwd=cwd):
                state = JSON.from_file(file, cwd=cwd, fallback={})
                return ProjectState(state=state, arguments=arguments, config=config)
            return ProjectState.from_empty(arguments=arguments, config=config)
        except SchemaError as ex:
            # raise InvalidStateError()
            raise ex
        except Exception as ex:
            raise ex

    @staticmethod
    def from_empty(arguments: Namespace, config):
        return ProjectState({
            "charts": {},
            "manifests": {}
        }, arguments=arguments, config=config)

    def to_file(self):
        JSON.to_file(
            filename=self.arguments.state,
            obj=self.to_state(),
            cwd=self.arguments.project,
            indent=2
        )

    def _create_key(self, *parts) -> str:
        parts_filtered = []
        for part in parts:
            if part and isinstance(part, str):
                parts_filtered.append(part)
        return "/".join(parts_filtered).strip().lower()

    def _create_manifest_key(self, manifest: ProjectStateManifest or ProjectConfigKubectlManifest) -> str:
        return self._create_key(manifest.get_identifier())

    def _create_chart_key(self, chart: ProjectStateChart or ProjectConfigHelmRelease) -> str:
        return self._create_key(chart.get_identifier())

    def has_manifest(self, manifest: ProjectStateManifest or ProjectConfigKubectlManifest) -> bool:
        return self._create_manifest_key(manifest) in self.state.get("manifests")

    def get_manifests(self) -> typing.List[ProjectStateManifest]:
        return self.state.get("manifests").values()

    def get_manifest(self, manifest: ProjectStateManifest or ProjectConfigKubectlManifest) -> ProjectStateManifest | None:
        key = self._create_manifest_key(manifest)
        return self.state["manifests"][key] if self.has_manifest(manifest) else None

    def set_manifest(self, manifest: ProjectStateManifest or ProjectConfigKubectlManifest) -> ProjectStateManifest:
        key = self._create_manifest_key(manifest)
        self.state["manifests"][key] = ProjectStateManifest(manifest.get_content(), config=self.config)
        return self.get_manifest(manifest)

    def remove_manifest(self, manifest: ProjectStateManifest or ProjectConfigKubectlManifest) -> bool:
        key = self._create_manifest_key(manifest)
        if self.has_manifest(manifest):
            del self.state["manifests"][key]
        return False

    def has_chart(self, chart: ProjectStateChart or ProjectConfigHelmRelease) -> bool:
        return self._create_chart_key(chart) in self.state.get("charts")

    def get_charts(self) -> typing.List[ProjectStateChart]:
        return self.state.get("charts").values()

    def get_chart(self, chart: ProjectStateChart or ProjectConfigHelmRelease) -> ProjectStateChart | None:
        key = self._create_chart_key(chart)
        return self.state["charts"][key] if self.has_chart(chart) else None

    def set_chart(self, chart: ProjectStateChart or ProjectConfigHelmRelease) -> ProjectStateChart:
        key = self._create_chart_key(chart)
        self.state["charts"][key] = ProjectStateChart(data=chart.to_dict(), config=self.config)
        return self.get_chart(chart)

    def remove_chart(self, chart: ProjectStateChart or ProjectConfigHelmRelease) -> bool:
        key = self._create_chart_key(chart)
        if self.has_manifest(chart):
            del self.state["charts"][key]
            self.to_file()
        return False

    def to_dict(self) -> dict:
        return self.state

    def to_state(self) -> dict:
        # create empty state
        state = {
            "charts": {},
            "manifests": {},
        }
        # add charts to state
        for chart in self.get_charts():
            state["charts"][self._create_chart_key(chart)] = chart.to_state()
        # add manifests to state
        for manifest in self.get_manifests():
            state["manifests"][self._create_manifest_key(manifest)] = manifest.to_state()
        # return state
        return state