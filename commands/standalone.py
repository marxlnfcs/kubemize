import os

from lib.helpers.commander import Commander, CommanderCommandForProject
from lib.helpers.filesystem import join_path, resolve_path
from lib.helpers.logging import Logger
from lib.helpers.object import reverse_array
from lib.helpers.script_builder import ScriptBuilder
from lib.helpers.yamls import YAML
from lib.plan.plan import ProjectPlan
from lib.project import Project


class CommandStandalone(CommanderCommandForProject):
    def __init__(self):
        super().__init__(
            name="standalone",
            description="Builds the project and stores all rendered files in the directory defined with argument '--output' to allow deployment without the kubemize cli."
        )

    def commands(self, commander: Commander):
        # output directory
        commander.add_argument(
            "-o", "--output",
            dest="output",
            help="Defines the output directory, where all rendered files will be stored",
            default=os.environ.get("KM_OUTPUT", default=join_path(os.getcwd(), "dist"))
        )

    def run(self, project: Project) -> any:
        # create plan
        plan = project.create_plan()
        # run hooks
        self._run_hooks(project, "pre")
        # create core variables
        output_dir: str = resolve_path(project.config.get_output_dir(), cwd=os.getcwd())
        manifests: list = []
        charts: list = []
        # render manifests
        if len(plan.get_expected_manifests()):
            Logger.info("Rendering {0} manifests...".format(len(plan.get_expected_manifests())))
            self._create_manifests(plan, manifests)
        # render charts
        if len(plan.get_expected_charts()):
            Logger.info("Rendering {0} charts...".format(len(plan.get_expected_charts())))
            self._create_charts(plan, charts)
        # writing manifest files
        Logger.info("Creating {0} manifest files...".format(len(manifests)))
        self._write_resources(output_dir, manifests)
        # writing chart files
        Logger.info("Creating {0} chart values...".format(len(charts)))
        self._write_resources(output_dir, charts)
        # writing scripts
        Logger.info("Creating scripts...")
        self._create_scripts(project, output_dir, manifests, charts)
        # run hooks
        self._run_hooks(project, "post")

    def _run_hooks(self, project: Project, hook_type: str):
        if hook_type == "pre":
            project.get_hooks_runner().run_hooks_pre_all()
            project.get_hooks_runner().run_hooks_pre_standalone()
        elif hook_type == "post":
            project.get_hooks_runner().run_hooks_post_all()
            project.get_hooks_runner().run_hooks_post_standalone()

    def _create_manifests(self, plan: ProjectPlan, manifests: list):
        for state in plan.get_expected_manifests():
            # get manifest and it's kind
            manifest = state.get_manifest()
            # add manifest to content
            manifests.append({
                "path": "manifests/{0}.yaml".format(manifest.get_identifier()),
                "item": manifest,
                "content": manifest.get_content()
            })
            # log completeness
            Logger.success(("Rendered manifest '{0}' of kind '{1}' in namespace '{2}'." if manifest.get_namespace() else "Rendered manifest '{0}' of kind '{1}'.").format(manifest.get_name(), manifest.get_kind(), manifest.get_namespace()))

    def _create_charts(self, plan: ProjectPlan, charts: list):
        for state in plan.get_expected_charts():
            # get chart and it's identifier
            chart = state.get_chart()
            # create chart in dict if not exist
            charts.append({
                "path": "charts/values_{0}_{1}.yaml".format(chart.get_namespace(), chart.get_name()),
                "item": chart,
                "content": chart.get_values(),
            })
            # log completeness
            Logger.success(("Rendered chart '{0}' in namespace '{1}'.").format(chart.get_name(), chart.get_namespace()))

    def _write_resources(self, output_dir: str, resources: list):
        for resource in resources:
            resource_path = resolve_path(resource["path"], cwd=output_dir)
            YAML.to_file(resource_path, resource["content"])
            Logger.success("Created file '{0}'...".format(resource_path))


    def _create_scripts(self, project: Project, output_dir: str, manifests: list, charts: list):
        self._create_scripts_apply(project, output_dir, manifests, charts)
        self._create_script_destroy(project, output_dir, manifests, charts)

    def _create_scripts_apply(self, project: Project, output_dir: str, manifests: list, charts: list):
        # create script builders
        builders = [
            ScriptBuilder(platform="windows"),
            ScriptBuilder(platform="linux"),
        ]
        # create commands for every builder
        for builder in builders:
            # create manifest commands
            builder.add_comment([
                "=====================================================",
                "===================== Manifests =====================",
                "=====================================================",
            ])
            builder.newline()
            for manifest in manifests:
                comment = ("Performing create or update of manifest '{0}' of kind '{1}' in namespace '{2}'." if manifest["item"].get_namespace() else "Performing create or update of manifest '{0}' of kind '{1}'.").format(manifest["item"].get_name(), manifest["item"].get_kind(), manifest["item"].get_namespace())
                builder.add(
                    comment=comment,
                    prints="{0}..".format(comment),
                    content=project.get_kubectl().create_apply_command(manifest["item"], manifest["path"]).to_string(),
                )
                builder.newline()
            # new lines
            builder.newline(2)
            # create chart commands
            builder.add_comment([
                "=====================================================",
                "======================= Charts ======================",
                "=====================================================",
            ])
            builder.newline()
            for chart in charts:
                comment = "Performing install/upgrade of chart '{0}' in namespace '{1}'.".format(chart["item"].get_name(), chart["item"].get_namespace())
                builder.add(
                    comment=comment,
                    prints="{0}..".format(comment),
                    content=project.get_helm().create_apply_command(chart["item"], chart["path"]).to_string(),
                )
                builder.newline()
            # log done message
            builder.add_print("Applied!")
            # save script
            Logger.success("Created script '{0}'.".format(builder.save("apply", cwd=output_dir)))


    def _create_script_destroy(self, project: Project, output_dir: str, manifests: list, charts: list):
        # create script builders
        builders = [
            ScriptBuilder(platform="windows"),
            ScriptBuilder(platform="linux"),
        ]
        # create commands for every builder
        for builder in builders:
            # create chart commands
            builder.add_comment([
                "=====================================================",
                "======================= Charts ======================",
                "=====================================================",
            ])
            builder.newline()
            for chart in reverse_array(list(charts)):
                comment = "Performing uninstall of chart '{0}' in namespace '{1}'.".format(chart["item"].get_name(), chart["item"].get_namespace())
                builder.add(
                    comment=comment,
                    prints="{0}..".format(comment),
                    content=project.get_helm().create_uninstall_command(chart["item"]).to_string(),
                )
                builder.newline()
            # new lines
            builder.newline(2)
            # create manifest commands
            builder.add_comment([
                "=====================================================",
                "===================== Manifests =====================",
                "=====================================================",
            ])
            builder.newline()
            for manifest in reverse_array(list(manifests)):
                comment = ("Performing delete of manifest '{0}' of kind '{1}' in namespace '{2}'." if manifest["item"].get_namespace() else "Performing delete of manifest '{0}' of kind '{1}'.").format(manifest["item"].get_name(), manifest["item"].get_kind(), manifest["item"].get_namespace())
                builder.add(
                    comment=comment,
                    prints="{0}..".format(comment),
                    content=project.get_kubectl().create_delete_command(manifest["item"], manifest["path"]).to_string(),
                )
                builder.newline()
            # log done message
            builder.add_print("Destroyed!")
            # save script
            Logger.success("Created script '{0}'.".format(builder.save("destroy", cwd=output_dir)))