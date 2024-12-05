import typing

from lib.config.parser.utils import ProjectConfigParserUtils
from lib.helpers.filesystem import resolve_path, file_exists
from lib.helpers.jsons import JSON
from lib.helpers.object import reverse_array, object_format_each_primitive
from lib.helpers.smart_merge import smart_merge


class ProjectConfigParserConfig:
    def __init__(self):
        self.utils: ProjectConfigParserUtils = ProjectConfigParserUtils()

    def parse(self, config: dict, config_file: str, cwd: str, variables: dict):
        # extract all configs from config
        configs = self.utils.extract_configs(config, cwd=cwd, variables=variables, global_config_path=config_file, config_path=config_file)
        # render all configs
        for index in range(len(configs)):
            configs[index]["content"] = self.utils.default_config(self.utils.render_str_or_dict(configs[index]["content"], variables=variables, source_file=configs[index]["path"]))
        # resolve config files
        configs = self._resolve_config_files(configs, cwd)
        # merge configs into one config
        config = self._merge_configs(configs)
        # normalize config
        config = self._normalize_config(config)
        # return config
        return config

    def _resolve_config_files(self, configs: typing.List[dict], cwd: str) -> typing.List[dict]:
        for config in configs:
            # resolve hooks
            for hook_type in ["all", "apply", "template", "standalone", "plan", "destroy"]:
                for hook_step in ["pre_{0}".format(hook_type), "post_{0}".format(hook_type)]:
                    config["content"]["hooks"][hook_step] = self.utils.resolve_file_patterns(JSON.get("content.hooks.{0}".format(hook_step), config, []), cwd)

            # resolve releases
            for release in config["content"]["helm"]["releases"]:
                # resolve values
                release["values"] = self.utils.resolve_file_patterns(JSON.get("values", release, []), config["cwd"])
                # resolve set
                for key in (release["set"] if "set" in release else {}):
                    item = release["set"][key]
                    if isinstance(item, dict):
                        if not JSON.has_path("type", item):
                            del release["set"][key]
                        elif JSON.get("type", item) == "file":
                            item["path"] = resolve_path(JSON.get("path", item), cwd=config["cwd"])
                            if not file_exists(item["path"]):
                                raise FileNotFoundError("Release '{0}' requires the file '{1}' that does not exists (--set-file={2}={1})", release["name"], item["path"], key)

            # resolve manifests
            config["content"]["kubectl"]["manifests"] = self.utils.resolve_file_patterns(config["content"]["kubectl"]["manifests"], cwd=config["cwd"])

            # resolve config maps
            for configMap in config["content"]["kubectl"]["generators"]["configMaps"]:
                for key in (configMap["data"] if JSON.isinstance("data", dict, configMap) else {}):
                    item = configMap["data"][key]
                    if isinstance(item, dict) and "type" in item and item["type"] == "file":
                        file = self.utils.resolve_file(item["path"], cwd=config["cwd"])
                        if not file_exists(file):
                            raise FileNotFoundError("SecretsGenerator: File '{0}' does not exist.".format(file))
                        item["path"] = file

            # resolve config maps
            for secret in config["content"]["kubectl"]["generators"]["secrets"]:
                for key in (secret["data"] if JSON.isinstance("data", dict, secret) else {}):
                    item = secret["data"][key]
                    if isinstance(item, dict) and "type" in item and item["type"] == "file":
                        file = self.utils.resolve_file(item["path"], cwd=config["cwd"])
                        if not file_exists(file):
                            raise FileNotFoundError("SecretsGenerator: File '{0}' does not exist.".format(file))
                        item["path"] = file

        # return configs
        return configs

    def _merge_configs(self, configs: typing.List[dict]) -> dict:
        # reverse configs
        configs = reverse_array(configs)
        # create empty config
        config = {}
        # merge configs
        for config_resource in configs:
            config = smart_merge(config, config_resource["content"])
        # return config
        return config

    def _normalize_config(self, config: dict) -> dict:
        def formatter(item: any):
            if isinstance(item, list):
                return reverse_array(item)
            return item
        return object_format_each_primitive(config, formatter)