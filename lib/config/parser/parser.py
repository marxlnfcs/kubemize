from argparse import Namespace

from lib.config.parser.config import ProjectConfigParserConfig
from lib.config.parser.variables import ProjectConfigParserVariables
from lib.errors.project_not_found import ProjectNotFoundError
from lib.helpers.filesystem import file_exists, resolve_path
from .generators import ProjectConfigParserGenerators
from .utils import ProjectConfigParserUtils
from ...helpers.jsons import JSON
from ...helpers.smart_merge import smart_merge
from ...helpers.template import Template


class ProjectConfigParser:
    def __init__(self, project_dir: str, project_config: str, arguments: Namespace):
        # throw error if project not exists
        if not file_exists(project_config, cwd=project_dir):
            raise ProjectNotFoundError(project_config, project_dir)
        # set global values
        self.project_dir: str = project_dir
        self.project_config: str = project_config
        # create helper classes
        self.utils: ProjectConfigParserUtils = ProjectConfigParserUtils()
        self.vars: ProjectConfigParserVariables = ProjectConfigParserVariables(arguments)
        self.config: ProjectConfigParserConfig = ProjectConfigParserConfig()
        self.generators: ProjectConfigParserGenerators = ProjectConfigParserGenerators()

    def parse(self) -> dict:
        # resolve config file
        config_file = resolve_path(self.project_config, cwd=self.project_dir)
        # load config
        config = self.utils.load_from_yaml(self.project_config, cwd=self.project_dir)
        # parse variables
        variables = self.vars.parse(config, config_file, cwd=self.project_dir)
        # parse config
        config = self.config.parse(config, config_file, cwd=self.project_dir, variables=variables)
        # validate config
        config = self.utils.validate_config(config, False)
        # parse config files
        config = self._render_config(config, variables=variables)
        # return config
        return config

    def _render_config(self, config: dict, variables: dict) -> dict:
        # render charts
        self._render_config_charts(config, variables=variables)
        # render manifests
        self._render_config_manifests(config, variables=variables)
        # render config maps
        self._render_config_configmaps(config, variables=variables)
        # render secrets
        self._render_config_secrets(config, variables=variables)
        # return config
        return config

    def _render_config_charts(self, config: dict, variables: dict):
        for release in config["helm"]["releases"]:
            values = {}
            for item in JSON.get("values", release, []):
                item_values = {}
                if isinstance(item, str):
                    item_values = Template.render_and_parse_yaml(item, data=variables)
                    self._validate_config_chart_values(item_values, item)
                values = smart_merge(values, item_values)
            release["values"] = values

    def _validate_config_chart_values(self, values: dict, values_file: str):
        pass

    def _render_config_manifests(self, config: dict, variables: dict):
        manifests = []
        for manifest_file in config["kubectl"]["manifests"]:
            for manifest_collection in Template.render_and_parse_all_yaml(manifest_file, data=variables):
                for manifest in self.utils.normalize_manifests(manifest_collection):
                    self._validate_config_manifest(manifest, manifest_file)
                    manifests.append(manifest)
        config["kubectl"]["manifests"] = manifests

    def _validate_config_manifest(self, manifest: dict, manifest_file: str):
        if not isinstance(manifest, dict):
            raise TypeError("Invalid manifest under '{0}' detected.".format(manifest_file))
        if not JSON.has_path_all_and_not_empty(["apiVersion", "kind", "metadata.name"], manifest):
            raise TypeError("Invalid manifest under '{0}' detected.".format(manifest_file))

    def _render_config_configmaps(self, config: dict, variables: dict):
        items = self.generators.generate_configmaps(config, variables=variables)
        for index in range(len(items)):
            self._validate_config_manifest(items[index], "kubectl.generators.configMaps[{0}]".format(index))
            config["kubectl"]["manifests"].append(items[index])

    def _render_config_secrets(self, config: dict, variables: dict):
        items = self.generators.generate_secrets(config, variables=variables)
        for index in range(len(items)):
            self._validate_config_manifest(items[index], "kubectl.generators.secrets[{0}]".format(index))
            config["kubectl"]["manifests"].append(items[index])