import os
from argparse import Namespace

from lib.helpers.commander import Commander, CommanderCommandForProject
from lib.helpers.logging import Logger
from lib.plan.plan import ProjectPlan
from lib.project import Project


class CommandPlan(CommanderCommandForProject):
    def __init__(self):
        super().__init__(
            name="plan",
            description="Plans and prints the changes"
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

    def run(self, project: Project) -> any:
        # create plan
        plan = project.create_plan()
        # run hooks
        project.get_hooks_runner().run_hooks_pre_all()
        project.get_hooks_runner().run_hooks_pre_plan()
        # process manifests
        self.run_manifests(plan, project.arguments)
        # process charts
        self.run_charts(plan, project.arguments)
        # run hooks
        project.get_hooks_runner().run_hooks_post_all()
        project.get_hooks_runner().run_hooks_post_plan()

    def run_charts(self, plan: ProjectPlan, arguments: Namespace) -> any:
        # updating charts
        for c in plan.get_updated_charts():
            chart = c.get_chart()
            Logger.info("{0}: Chart '{1}' in namespace '{2}':".format(Logger.colors().terminalBlue("UPDATE") + Logger.colors().end('') + Logger.colors().terminalBlue(''), chart.get_name(), chart.get_namespace()))

        # creating charts
        for c in plan.get_added_charts():
            chart = c.get_chart()
            Logger.info("{0}: Chart '{1}' in namespace '{2}':".format(Logger.colors().terminalGreen("CREATE") + Logger.colors().end('') + Logger.colors().terminalBlue(''), chart.get_name(), chart.get_namespace()))

        # deleting charts
        for c in plan.get_removed_charts():
            chart = c.get_chart()
            Logger.info("{0}: Chart '{1}' in namespace '{2}':".format(Logger.colors().terminalRed("DELETE") + Logger.colors().end('') + Logger.colors().terminalRed(''), chart.get_name(), chart.get_namespace()))

    def run_manifests(self, plan: ProjectPlan, arguments: Namespace) -> any:
        # updating manifests
        for m in plan.get_updated_manifests():
            manifest = m.get_manifest()
            if manifest.get_namespace():
                Logger.info("{0}: {1} '{2}' in namespace '{3}'".format(Logger.colors().terminalBlue("UPDATE") + Logger.colors().end('') + Logger.colors().terminalBlue(''), manifest.get_kind(), manifest.get_name(), manifest.get_namespace()))
            else:
                Logger.info("{0}: {1} '{2}'".format(Logger.colors().terminalBlue("UPDATE") + Logger.colors().end('') + Logger.colors().terminalBlue(''), manifest.get_kind(), manifest.get_name()))

        # creating manifests
        for m in plan.get_added_manifests():
            manifest = m.get_manifest()
            if manifest.get_namespace():
                Logger.info("{0}: {1} '{2}' in namespace '{3}'".format(Logger.colors().terminalGreen("CREATE") + Logger.colors().end('') + Logger.colors().terminalBlue(''), manifest.get_kind(), manifest.get_name(), manifest.get_namespace()))
            else:
                Logger.info("{0}: {1} '{2}'".format(Logger.colors().terminalGreen("CREATE") + Logger.colors().end('') + Logger.colors().terminalBlue(''), manifest.get_kind(), manifest.get_name()))

        # deleting manifests
        for m in plan.get_removed_manifests():
            manifest = m.get_manifest()
            if manifest.get_namespace():
                Logger.info("{0}: {1} '{2}' in namespace '{3}'".format(Logger.colors().terminalRed("DELETE") + Logger.colors().end('') + Logger.colors().terminalRed(''), manifest.get_kind(), manifest.get_name(), manifest.get_namespace()))
            else:
                Logger.info("{0}: {1} '{2}'".format(Logger.colors().terminalRed("DELETE") + Logger.colors().end('') + Logger.colors().terminalRed(''), manifest.get_kind(), manifest.get_name()))
