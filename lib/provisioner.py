import typing
from typing import TYPE_CHECKING

from lib.helpers.helm import Helm
from lib.helpers.kubectl import Kubectl
from lib.helpers.logging import Logger
from lib.state.schemes.chart import ProjectStateChart
from lib.state.schemes.manifest import ProjectStateManifest
from lib.state.state import ProjectState

if TYPE_CHECKING:
    from lib.project import Project

class ProjectProvisioner:
    def __init__(self, project: "Project", state: ProjectState):
        self.state: ProjectState = state
        self.helm: Helm = project.get_helm()
        self.kubectl: Kubectl = project.get_kubectl()
        self.resources_created: int = 0
        self.resources_updated: int = 0
        self.resources_deleted: int = 0
        self.resources_failed: int = 0

    def _run_command(self, command_func: typing.Callable, logger_indent: int = 0, **command_args) -> bool:
        for line in command_func(**command_args):
            if line["type"] == "command":
                Logger.debug("$ {0}".format(line["data"]), indent=logger_indent+1)
                Logger.debug("-----", indent=logger_indent+1)
            elif line["type"] == "data":
                Logger.debug(line["data"], indent=logger_indent+1)
            elif line["type"] == "error":
                Logger.error(line["data"], indent=logger_indent+1)
            elif line["type"] == "code":
                if line["data"] != 0:
                    return False
        return True

    def install_chart(self, chart: ProjectStateChart, logger_indent: int = 0, values_file: str = None) -> bool:
        # log information
        Logger.info("- Installing chart '{0}' in namespace '{1}'...".format(chart.get_name(), chart.get_namespace()), indent=logger_indent)
        # install chart
        if not self._run_command(self.helm.apply, logger_indent=logger_indent, release=chart, values_file=values_file):
            self.resources_failed = self.resources_failed + 1
            Logger.fatal("- Could not install chart '{0}' in namespace '{1}'.".format(chart.get_name(), chart.get_namespace()), indent=logger_indent)
            return False
        # chart has been installed
        self.state.set_chart(chart)
        self.resources_created = self.resources_created + 1
        Logger.success("- Chart '{0}' in namespace '{1}' has been installed.".format(chart.get_name(), chart.get_namespace()), indent=logger_indent)
        return True

    def upgrade_chart(self, chart: ProjectStateChart, old_chart: ProjectStateChart, logger_indent: int = 0, values_file: str = None):
        # log information
        Logger.info("- Upgrading chart '{0}' in namespace '{1}'...".format(chart.get_name(), chart.get_namespace()), indent=logger_indent)
        # upgrade chart
        if not self._run_command(self.helm.apply, logger_indent=logger_indent, release=chart, values_file=values_file):
            self.resources_failed = self.resources_failed + 1
            Logger.fatal("- Could not upgrade chart '{0}' in namespace '{1}'.".format(chart.get_name(), chart.get_namespace()), indent=logger_indent)
            self.state.set_chart(old_chart)
            return False
        # chart has been upgraded
        self.state.set_chart(chart)
        self.resources_updated = self.resources_updated + 1
        Logger.success("- Chart '{0}' in namespace '{1}' has been upgraded.".format(chart.get_name(), chart.get_namespace()), indent=logger_indent)
        return True

    def uninstall_chart(self, chart: ProjectStateChart, logger_indent: int = 0):
        # log information
        Logger.info("- Uninstalling chart '{0}' in namespace '{1}'...".format(chart.get_name(), chart.get_namespace()), indent=logger_indent)
        # uninstall chart
        if not self._run_command(self.helm.uninstall, logger_indent=logger_indent, release=chart):
            self.resources_failed = self.resources_failed + 1
            Logger.fatal("- Could not uninstall chart '{0}' in namespace '{1}'.".format(chart.get_name(), chart.get_namespace()), indent=logger_indent)
            self.state.set_chart(chart)
            return False
        # chart has been uninstalled
        self.state.remove_chart(chart)
        self.resources_deleted = self.resources_deleted + 1
        Logger.success("- Chart '{0}' in namespace '{1}' has been uninstalled.".format(chart.get_name(), chart.get_namespace()), indent=logger_indent)
        return True

    def create_manifest(self, manifest: ProjectStateManifest, logger_indent: int = 0, manifest_file: str = None) -> bool:
        # log information
        Logger.info(
            ("- Creating {0} '{1}' in namespace '{2}'..." if manifest.get_namespace() else "- Creating {0} '{1}'...")
            .format(manifest.get_kind(), manifest.get_name(), manifest.get_namespace()),
            indent=logger_indent
        )
        # create manifest
        if not self._run_command(self.kubectl.apply, logger_indent=logger_indent, manifest=manifest, manifest_file=manifest_file):
            self.resources_failed = self.resources_failed + 1
            Logger.fatal(
                ("- Could not create {0} '{1}' in namespace '{2}'." if manifest.get_namespace() else "- Could not create {0} '{1}'.")
                .format(manifest.get_kind(), manifest.get_name(), manifest.get_namespace()),
                indent=logger_indent
            )
            return False
        # manifest has been created
        self.state.set_manifest(manifest)
        self.resources_created = self.resources_created + 1
        Logger.success(
            ("- {0} '{1}' in namespace '{2}' has been created." if manifest.get_namespace() else "- {0} '{1}' has been created.")
            .format(manifest.get_kind(), manifest.get_name(), manifest.get_namespace()),
            indent=logger_indent
        )
        return True

    def update_manifest(self, manifest: ProjectStateManifest, old_manifest: ProjectStateManifest, logger_indent: int = 0, manifest_file: str = None):
        # log information
        Logger.info(
            ("- Updating {0} '{1}' in namespace '{2}'..." if manifest.get_namespace() else "- Updating {0} '{1}'...")
            .format(manifest.get_kind(), manifest.get_name(), manifest.get_namespace()),
            indent=logger_indent
        )
        # update manifest
        if not self._run_command(self.kubectl.apply, logger_indent=logger_indent, manifest=manifest, manifest_file=manifest_file):
            self.resources_failed = self.resources_failed + 1
            Logger.fatal(
                ("- Could not update {0} '{1}' in namespace '{2}'." if manifest.get_namespace() else "- Could not update {0} '{1}'.")
                .format(manifest.get_kind(), manifest.get_name(), manifest.get_namespace()),
                indent=logger_indent
            )
            self.state.set_manifest(old_manifest)
            return False
        # manifest has been updated
        self.state.set_manifest(manifest)
        self.resources_updated = self.resources_updated + 1
        Logger.success(
            ("- {0} '{1}' in namespace '{2}' has been updated." if manifest.get_namespace() else "- {0} '{1}' has been updated.")
            .format(manifest.get_kind(), manifest.get_name(), manifest.get_namespace()),
            indent=logger_indent
        )
        return True

    def delete_manifest(self, manifest: ProjectStateManifest, logger_indent: int = 0, manifest_file: str = None):
        # log information
        Logger.info(
            ("- Deleting {0} '{1}' in namespace '{2}'..." if manifest.get_namespace() else "- Deleting {0} '{1}'...")
            .format(manifest.get_kind(), manifest.get_name(), manifest.get_namespace()),
            indent=logger_indent
        )
        # delete manifest
        if not self._run_command(self.kubectl.delete, logger_indent=logger_indent, manifest=manifest, manifest_file=manifest_file):
            self.resources_failed = self.resources_failed + 1
            Logger.fatal(
                ("- Could not delete {0} '{1}' in namespace '{2}'." if manifest.get_namespace() else "- Could not delete {0} '{1}'.")
                .format(manifest.get_kind(), manifest.get_name(), manifest.get_namespace()),
                indent=logger_indent
            )
            self.state.set_manifest(manifest)
            return False
        # manifest has been deleted
        self.state.remove_manifest(manifest)
        self.resources_deleted = self.resources_deleted + 1
        Logger.success(
            ("- {0} '{1}' in namespace '{2}' has been deleted." if manifest.get_namespace() else "- {0} '{1}' has been deleted.")
            .format(manifest.get_kind(), manifest.get_name(), manifest.get_namespace()),
            indent=logger_indent
        )
        return True

    def get_resources_total(self) -> int:
        return self.resources_created + self.resources_updated + self.resources_deleted + self.resources_failed

    def get_resources_created(self) -> int:
        return self.resources_created

    def get_resources_updated(self) -> int:
        return self.resources_updated

    def get_resources_deleted(self) -> int:
        return self.resources_deleted

    def get_resources_failed(self) -> int:
        return self.resources_failed