import os

from lib.helpers.commander import Commander, CommanderCommandForProject
from lib.helpers.filesystem import delete_dir
from lib.helpers.logging import Logger
from lib.plan.plan import ProjectPlan
from lib.project import Project
from lib.provisioner import ProjectProvisioner


class CommandApply(CommanderCommandForProject):
    def __init__(self):
        super().__init__(
            name="apply",
            description="Applies the current configuration"
        )

    def commands(self, commander: Commander):
        # force
        commander.add_argument(
            "--force",
            dest="force",
            help="Applies all manifests even if they have not been changed.",
            action="store_true",
            default=os.environ.get("FM_FORCE", default=False)
        )

    def run(self, project: Project):
        # create plan
        plan = project.create_plan()
        # skip if nothing to do
        if not plan.get_processable_resources():
            return Logger.success("Nothing to change. Your infrastructure is up to date. If you want to re-apply everything, run the command with the --force argument.")
        # create provisioner to apply the plan
        provisioner = project.create_provisioner()
        # run hooks
        project.get_hooks_runner().run_hooks_pre_all()
        project.get_hooks_runner().run_hooks_pre_apply()
        # provision manifests
        if self.provision_manifests(plan, provisioner):
            # provision charts
            self.provision_charts(plan, provisioner)
        # done
        self.finalize(project, provisioner)

    def provision_manifests(self, plan: ProjectPlan, provisioner: ProjectProvisioner) -> bool:
        # log information
        if plan.get_processable_manifests():
            Logger.info("Processing {0} manifests...".format(len(plan.get_processable_manifests())))
        # add unchanged manifests to state
        for manifest in plan.get_unchanged_manifests():
            provisioner.state.set_manifest(manifest.get_manifest())
        # delete manifests
        for manifest in plan.get_removed_manifests():
            if not provisioner.delete_manifest(manifest.get_manifest(), logger_indent=0):
                return False
        # create manifests
        for manifest in plan.get_added_manifests():
            if not provisioner.create_manifest(manifest.get_manifest(), logger_indent=0):
                return False
        # update manifests
        for manifest in plan.get_updated_manifests():
            if not provisioner.update_manifest(manifest.get_manifest(), manifest.get_current_manifest(), logger_indent=0):
                return False
        # done
        return True

    def provision_charts(self, plan: ProjectPlan, provisioner: ProjectProvisioner) -> bool:
        # log information
        if plan.get_processable_charts():
            Logger.info("Processing {0} charts...".format(len(plan.get_processable_charts())))
        # add unchanged charts to state
        for chart in plan.get_unchanged_charts():
            provisioner.state.set_chart(chart.get_chart())
        # delete charts
        for chart in plan.get_removed_charts():
            if not provisioner.uninstall_chart(chart.get_chart(), logger_indent=0):
                return False
        # install charts
        for chart in plan.get_added_charts():
            if not provisioner.install_chart(chart.get_chart(), logger_indent=0):
                return False
        # upgrade charts
        for chart in plan.get_updated_charts():
            if not provisioner.upgrade_chart(
                    chart=chart.get_chart(),
                    old_chart=chart.get_current_chart(),
                    logger_indent=0
            ):
                return False
        # done
        return True

    def finalize(self, project: Project, provisioner: ProjectProvisioner):
        # run hooks
        project.get_hooks_runner().run_hooks_post_all()
        project.get_hooks_runner().run_hooks_post_apply()
        # log information
        if not provisioner.get_resources_failed():
            Logger.success("Applied! {0} Created, {1} Updated, {2} Deleted.".format(provisioner.resources_created, provisioner.resources_updated, provisioner.resources_deleted))
        else:
            Logger.warn("Applied with errors! {0} Created, {1} Updated, {2} Deleted.".format(provisioner.resources_created, provisioner.resources_updated, provisioner.resources_deleted))
        # save state file
        project.get_new_state().to_file()
        # delete output dir
        if project.config.get_output_dir() != project.arguments.project:
            delete_dir(project.config.get_output_dir())