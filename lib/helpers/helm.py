import os

from lib.helpers.command_builder import CommandBuilder
from lib.helpers.filesystem import resolve_path
from lib.helpers.yamls import YAML
from lib.state.schemes.chart import ProjectStateChart


class Helm:
    def __init__(self, executable: str = None, cwd: str = None):
        self.executable: str = executable if executable is not None else "helm"
        self.cwd: str = cwd

    def _get_command_builder(self) -> CommandBuilder:
        builder = CommandBuilder(command=self.executable, cwd=self.cwd)
        return builder

    def update_repositories(self, silence: bool = False):
        try:
            builder = self._get_command_builder()
            builder.add_command("repo", "update")
            for line in builder.execute():
                yield line
        except Exception as ex:
            if not silence:
                raise ex

    def _create_values_file(self, release: ProjectStateChart, values_file: str) -> str:
        return values_file if values_file is not None else resolve_path("chart-values/{0}".format(release.get_identifier()), cwd=release.config.get_output_dir())

    def create_apply_command(self, release: ProjectStateChart, values_file: str = None) -> CommandBuilder:
        # create builder
        builder = self._get_command_builder()
        # set command and base arguments
        builder.add_command("upgrade", release.get_name(), release.get_chart())
        builder.add_argument("--version", release.get_version())
        builder.add_argument("--install", True)
        builder.add_argument("--namespace", release.get_namespace())
        builder.add_argument("--create-namespace", True)
        # set global arguments
        for item in release.get_arguments().globally().get_arguments():
            if isinstance(item["value"], list):
                for value in item["value"]:
                    builder.add_argument(item["key"], value, True)
            else:
                builder.add_argument(item["key"], item["value"])
        # set apply arguments
        for item in release.get_arguments().apply().get_arguments():
            if isinstance(item["value"], list):
                for value in item["value"]:
                    builder.add_argument(item["key"], value, True)
            else:
                builder.add_argument(item["key"], item["value"])
        # add repository details
        builder.add_argument("--repo", release.get_repository_url() if not release.is_oci() else release.get_repository_url())
        builder.add_argument("--username", release.get_repository_username())
        builder.add_argument("--password", release.get_repository_password())
        builder.add_argument("--pass-credentials", release.get_repository_pass_credentials())
        builder.add_argument("--ca-file", release.get_repository_ca_file())
        builder.add_argument("--cert-file", release.get_repository_cert_file())
        builder.add_argument("--key-file", release.get_repository_key_file())
        builder.add_argument("--keyring", release.get_repository_key_ring())
        builder.add_argument("--verify", release.get_repository_verify())
        # set values file
        builder.add_argument("-f", self._create_values_file(release, values_file))
        # return builder
        return builder

    def apply(self, release: ProjectStateChart, values_file: str = None):
        # create temporary values filename
        values_file = self._create_values_file(release, values_file)
        # create temporary values file
        YAML.to_file(filename=values_file, obj=release.get_values())
        # execute command
        for line in self.create_apply_command(release, values_file).execute():
            yield line
        # delete temporary values file
        os.remove(values_file)

    def create_uninstall_command(self, release: ProjectStateChart) -> CommandBuilder:
        # create builder
        builder = self._get_command_builder()
        # set command and base arguments
        builder.add_command("uninstall", release.get_name())
        builder.add_argument("--namespace", release.get_namespace())
        builder.add_argument("--ignore-not-found", release.config.ignore_not_found())
        builder.add_argument("--wait", True)
        # set global arguments
        for item in release.get_arguments().globally().get_arguments():
            if isinstance(item["value"], list):
                for value in item["value"]:
                    builder.add_argument(item["key"], value, True)
            else:
                builder.add_argument(item["key"], item["value"])
        # set destroy arguments
        for item in release.get_arguments().destroy().get_arguments():
            if isinstance(item["value"], list):
                for value in item["value"]:
                    builder.add_argument(item["key"], value, True)
            else:
                builder.add_argument(item["key"], item["value"])
        # return builder
        return builder

    def uninstall(self, release: ProjectStateChart):
        # uninstall release
        for line in self.create_uninstall_command(release).execute():
            yield line
