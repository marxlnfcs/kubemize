import os

from lib.helpers.command_builder import CommandBuilder
from lib.helpers.filesystem import resolve_path
from lib.helpers.yamls import YAML
from lib.state.schemes.manifest import ProjectStateManifest


class Kubectl:
    def __init__(self, executable: str = None, cwd: str = None):
        self.executable: str = executable if executable is not None else "kubectl"
        self.cwd: str = cwd

    def _get_command_builder(self) -> CommandBuilder:
        builder = CommandBuilder(command=self.executable, cwd=self.cwd)
        return builder

    def _create_manifests_file(self, manifest: ProjectStateManifest, manifest_file: str) -> str:
        return manifest_file if manifest_file is not None else resolve_path("manifests/{0}".format(manifest.get_identifier()), cwd=manifest.config.get_output_dir())

    def create_apply_command(self, manifest: ProjectStateManifest, manifest_file: str) -> CommandBuilder:
        # create builder
        builder = self._get_command_builder()
        # set command and base arguments
        builder.add_command("apply")
        # set global arguments
        for item in manifest.get_arguments().globally().get_arguments():
            if isinstance(item["value"], list):
                for value in item["value"]:
                    builder.add_argument(item["key"], value, True)
            else:
                builder.add_argument(item["key"], item["value"])
        # set apply arguments
        for item in manifest.get_arguments().apply().get_arguments():
            if isinstance(item["value"], list):
                for value in item["value"]:
                    builder.add_argument(item["key"], value, True)
            else:
                builder.add_argument(item["key"], item["value"])
        # set manifest file
        builder.add_argument("-f", self._create_manifests_file(manifest, manifest_file))
        # return builder
        return builder


    def apply(self, manifest: ProjectStateManifest, manifest_file: str = None):
        # create temporary manifest filename
        manifest_file = self._create_manifests_file(manifest, manifest_file)
        # create temporary manifest file
        YAML.to_file(filename=manifest_file, obj=manifest.get_content())
        # execute command
        for line in self.create_apply_command(manifest, manifest_file).execute():
            yield line
        # delete temporary manifest file
        os.remove(manifest_file)

    def create_delete_command(self, manifest: ProjectStateManifest, manifest_file: str) -> CommandBuilder:
        # create builder
        builder = self._get_command_builder()
        # set command and base arguments
        builder.add_command("delete")
        builder.add_argument("--ignore-not-found", manifest.config.ignore_not_found())
        # set global arguments
        for item in manifest.get_arguments().globally().get_arguments():
            if isinstance(item["value"], list):
                for value in item["value"]:
                    builder.add_argument(item["key"], value, True)
            else:
                builder.add_argument(item["key"], item["value"])
        # set destroy arguments
        for item in manifest.get_arguments().destroy().get_arguments():
            if isinstance(item["value"], list):
                for value in item["value"]:
                    builder.add_argument(item["key"], value, True)
            else:
                builder.add_argument(item["key"], item["value"])
        # set manifest file
        builder.add_argument("-f", self._create_manifests_file(manifest, manifest_file))
        # return builder
        return builder

    def delete(self, manifest: ProjectStateManifest, manifest_file: str = None):
        # create temporary manifest filename
        manifest_file = self._create_manifests_file(manifest, manifest_file)
        # create temporary manifest file
        YAML.to_file(filename=manifest_file, obj=manifest.get_content())
        # execute command
        for line in self.create_delete_command(manifest, manifest_file).execute():
            yield line
        # delete temporary manifest file
        os.remove(manifest_file)