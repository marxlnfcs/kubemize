import typing

from lib.builder.state import ProjectBuilderState
from lib.config.config import ProjectConfig
from lib.helpers.object import flatten_array, reverse_array
from lib.plan.schemes.chart import ProjectPlanChart
from lib.plan.schemes.manifest import ProjectPlanManifest
from lib.state.state import ProjectState


class ProjectPlan:
    def __init__(self, config: ProjectConfig, state_current: ProjectState, state_new: ProjectState or ProjectBuilderState):
        self.config: ProjectConfig = config
        self.state_current: ProjectState = state_current
        self.state_new: ProjectState = state_new

    def get_manifests(self) -> typing.List[ProjectPlanManifest]:
        manifests = []
        for new_manifest in self.state_new.get_manifests():
            if self.state_current.has_manifest(new_manifest):
                current_manifest = self.state_current.get_manifest(new_manifest)
                manifests.append(ProjectPlanManifest(
                    action="update" if ("force" in self.config.arguments and self.config.arguments.force) or current_manifest.get_checksum() != new_manifest.get_checksum() else "nothing",
                    manifest=new_manifest,
                    manifest_current=current_manifest,
                ))
            else:
                manifests.append(ProjectPlanManifest(
                    action="create",
                    manifest=new_manifest,
                ))
        for current_manifest in self.state_current.get_manifests():
            if not self.state_new.has_manifest(current_manifest):
                manifests.append(ProjectPlanManifest(
                    action="delete",
                    manifest=current_manifest,
                ))
        return self._sort_manifests(manifests)

    def _sort_manifests(self, manifests: typing.List[ProjectPlanManifest]) -> typing.List[ProjectPlanManifest]:
        # create array for items
        items: typing.List[ProjectPlanManifest] = []
        # sort items based on the order
        for order in self.config.get_kubectl_order():
            for item in manifests:
                manifest = item.get_manifest()
                if order == manifest.get_kind().strip().lower() or order == manifest.get_type().strip().lower():
                    if item not in items:
                        items.append(item)
        # sort all other items
        for item in manifests:
            if item not in items:
                items.append(item)
        # return items
        return items

    def get_charts(self) -> typing.List[ProjectPlanChart]:
        charts = []
        for new_chart in self.state_new.get_charts():
            if self.state_current.has_chart(new_chart):
                current_chart = self.state_current.get_chart(new_chart)
                charts.append(ProjectPlanChart(
                    action="update" if ("force" in self.config.arguments and self.config.arguments.force) or current_chart.get_checksum() != new_chart.get_checksum() else "nothing",
                    chart=new_chart,
                    chart_current=current_chart,
                ))
            else:
                charts.append(ProjectPlanChart(
                    action="create",
                    chart=new_chart,
                ))
        for current_chart in self.state_current.get_charts():
            if not self.state_new.has_chart(current_chart):
                charts.append(ProjectPlanChart(
                    action="delete",
                    chart=current_chart,
                ))
        return self._sort_charts(charts)
    def _sort_charts(self, charts: typing.List[ProjectPlanChart]) -> typing.List[ProjectPlanChart]:
        return charts

    def get_total_resources(self) -> typing.List[ProjectPlanManifest or ProjectPlanChart]:
        return flatten_array(self.get_total_manifests(), self.get_total_charts())

    def get_processable_resources(self) -> typing.List[ProjectPlanManifest or ProjectPlanChart]:
        return flatten_array(self.get_processable_manifests(), self.get_processable_charts())

    def get_expected_resources(self) -> typing.List[ProjectPlanManifest or ProjectPlanChart]:
        return flatten_array(self.get_expected_manifests(), self.get_expected_charts())

    def get_existing_resources(self) -> typing.List[ProjectPlanManifest or ProjectPlanChart]:
        return flatten_array(self.get_existing_manifests(), self.get_existing_charts())

    def get_unchanged_resources(self) -> typing.List[ProjectPlanManifest or ProjectPlanChart]:
        return flatten_array(self.get_unchanged_manifests(), self.get_unchanged_charts())

    def get_added_resources(self) -> typing.List[ProjectPlanManifest or ProjectPlanChart]:
        return flatten_array(self.get_added_manifests(), self.get_added_charts())

    def get_updated_resources(self) -> typing.List[ProjectPlanManifest or ProjectPlanChart]:
        return flatten_array(self.get_updated_manifests(), self.get_updated_charts())

    def get_removed_resources(self) -> typing.List[ProjectPlanManifest or ProjectPlanChart]:
        return flatten_array(self.get_removed_manifests(), self.get_removed_charts())

    def get_total_manifests(self) -> typing.List[ProjectPlanManifest]:
        return [item for item in self.get_manifests()]

    def get_processable_manifests(self) -> typing.List[ProjectPlanManifest]:
        return [item for item in self.get_manifests() if item.is_action("create", "update", "delete")]

    def get_expected_manifests(self) -> typing.List[ProjectPlanManifest]:
        return [item for item in self.get_manifests() if item.is_action("nothing", "create", "update")]

    def get_existing_manifests(self) -> typing.List[ProjectPlanManifest]:
        return [item for item in self.get_manifests() if item.is_action("nothing", "update")]

    def get_unchanged_manifests(self) -> typing.List[ProjectPlanManifest]:
        return [item for item in self.get_manifests() if item.is_action("nothing")]

    def get_added_manifests(self) -> typing.List[ProjectPlanManifest]:
        return [item for item in self.get_manifests() if item.is_action("create")]

    def get_updated_manifests(self) -> typing.List[ProjectPlanManifest]:
        return [item for item in self.get_manifests() if item.is_action("update")]

    def get_removed_manifests(self) -> typing.List[ProjectPlanManifest]:
        return reverse_array([item for item in self.get_manifests() if item.is_action("delete")])

    def get_total_charts(self) -> typing.List[ProjectPlanChart]:
        return [item for item in self.get_charts()]

    def get_processable_charts(self) -> typing.List[ProjectPlanChart]:
        return [item for item in self.get_charts() if item.is_action("create", "update", "delete")]

    def get_expected_charts(self) -> typing.List[ProjectPlanChart]:
        return [item for item in self.get_charts() if item.is_action("nothing", "create", "update")]

    def get_existing_charts(self) -> typing.List[ProjectPlanChart]:
        return [item for item in self.get_charts() if item.is_action("nothing", "update")]

    def get_unchanged_charts(self) -> typing.List[ProjectPlanChart]:
        return [item for item in self.get_charts() if item.is_action("nothing")]

    def get_added_charts(self) -> typing.List[ProjectPlanChart]:
        return [item for item in self.get_charts() if item.is_action("create")]

    def get_updated_charts(self) -> typing.List[ProjectPlanChart]:
        return [item for item in self.get_charts() if item.is_action("update")]

    def get_removed_charts(self) -> typing.List[ProjectPlanChart]:
        return reverse_array([item for item in self.get_charts() if item.is_action("delete")])
