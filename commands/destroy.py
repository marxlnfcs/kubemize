import os

from lib.helpers.commander import Commander, CommanderCommandForProject
from lib.helpers.filesystem import delete_dir
from lib.helpers.logging import Logger
from lib.helpers.object import reverse_array
from lib.plan.plan import ProjectPlan
from lib.project import Project
from lib.provisioner import ProjectProvisioner


class CommandDestroy(CommanderCommandForProject):
    def __init__(self):
        super().__init__(
            name="destroy",
            description="Destroys the applied configuration"
        )

    def commands(self, commander: Commander):
        # ignore-not-found
        commander.add_argument(
            "--ignore-not-found",
            dest="ignore_not_found",
            help="Adds the '--ignore-not-found' argument to the kubectl and helm commands. Treat 'resource not found' or 'release not found' as a successful delete.",
            action="store_true",
            default=os.environ.get("FM_IGNORE_NOT_FOUND", default=False)
        )

    def run(self, project: Project):
        # create plan
        plan = project.create_plan()
        # create provisioner to apply the plan
        provisioner = project.create_provisioner()
        # run hooks
        project.get_hooks_runner().run_hooks_pre_all()
        project.get_hooks_runner().run_hooks_pre_destroy()
        # provision charts
        self.provision_charts(plan, provisioner)
        # provision manifests
        self.provision_manifests(plan, provisioner)
        # done
        self.finalize(project, provisioner)

    def provision_manifests(self, plan: ProjectPlan, provisioner: ProjectProvisioner):
        # skip if no manifests to delete exists
        if len(plan.get_existing_manifests()) == 0:
            return True
        # log information
        Logger.info("Processing {0} manifests...".format(len(plan.get_existing_manifests())))
        # delete manifests
        for manifest in plan.get_removed_manifests():
            if not provisioner.delete_manifest(manifest.get_manifest()):
                return False
        for manifest in reverse_array(plan.get_existing_manifests()):
            if not provisioner.delete_manifest(manifest.get_manifest()):
                return False
        # done
        return True

    def provision_charts(self, plan: ProjectPlan, provisioner: ProjectProvisioner):
        # skip if no charts to delete exists
        if len(plan.get_existing_charts()) == 0:
            return True
        # log information
        Logger.info("Processing {0} charts...".format(len(plan.get_existing_charts())))
        # uninstall charts
        for chart in plan.get_removed_charts():
            if not provisioner.uninstall_chart(chart.get_chart()):
                return False
        for chart in reverse_array(plan.get_existing_charts()):
            if not provisioner.uninstall_chart(chart.get_chart()):
                return False
        # done
        return True

    def finalize(self, project: Project, provisioner: ProjectProvisioner):
        # log information
        if not provisioner.get_resources_failed():
            Logger.success("Destroyed! {0} Deleted.".format(provisioner.resources_deleted))
        else:
            Logger.warn("Destroyed with errors! {0} Deleted.".format(provisioner.resources_deleted))
        # run hooks
        project.get_hooks_runner().run_hooks_post_all()
        project.get_hooks_runner().run_hooks_post_destroy()
        # save state file
        project.get_new_state().to_file()
        # delete output dir
        if project.config.get_output_dir() != project.arguments.project:
            delete_dir(project.config.get_output_dir())