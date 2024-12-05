import os

from lib.helpers.commander import Commander, CommanderCommandForProject
from lib.helpers.filesystem import join_path, create_dir, resolve_path
from lib.helpers.logging import Logger
from lib.helpers.yamls import YAML
from lib.project import Project


class CommandTemplate(CommanderCommandForProject):
    def __init__(self):
        super().__init__(
            name="template",
            description="Renders all project files and stores it in the output directory"
        )

    def commands(self, commander: Commander):
        # output directory
        commander.add_argument(
            "-o", "--output",
            dest="output",
            help="Defines the output directory, where all rendered files will be stored",
            default=os.environ.get("KM_OUTPUT", default=join_path(os.getcwd(), ".tmp"))
        )

    def run(self, project: Project) -> any:
        # create plan
        plan = project.create_plan()
        # run hooks
        project.get_hooks_runner().run_hooks_pre_all()
        project.get_hooks_runner().run_hooks_pre_template()
        # create output directory
        output = create_dir(project.config.get_output_dir(), cwd=os.getcwd())
        # create charts and manifests dirs
        output_charts = create_dir("charts", cwd=output)
        output_manifests = create_dir("manifests", cwd=output)
        # write project config to filesystem
        Logger.info("Rendering project...")
        project_file = resolve_path("kubemize.yaml", cwd=output)
        YAML.to_file(filename=project_file, obj=project.config.to_dict())
        Logger.success("- Created project file: {0}".format(project_file))
        # write manifests to filesystem
        Logger.info("Rendering {0} manifests...".format(len(plan.get_expected_manifests())))
        for m in plan.get_expected_manifests():
            manifest = m.get_manifest()
            filename = resolve_path(manifest.get_identifier(include_namespace=False) + ".yaml", cwd=output_manifests)
            YAML.to_file(filename=filename, obj=manifest.get_content())
            Logger.success("- Created manifest: {0}".format(filename))
        # write chart values to filesystem
        Logger.info("Rendering {0} charts...".format(len(plan.get_expected_charts())))
        for c in plan.get_expected_charts():
            chart = c.get_chart()
            chart_dir = create_dir(chart.get_identifier(), cwd=output_charts)
            chart_values = resolve_path("values.yaml", cwd=chart_dir)
            YAML.to_file(filename=chart_values, obj=chart.get_values())
            Logger.success("- Created values for chart '{0}' in namespace '{1}': {2}".format(chart.get_name(), chart.get_namespace(), chart_values))
        # run hooks
        project.get_hooks_runner().run_hooks_post_all()
        project.get_hooks_runner().run_hooks_post_template()