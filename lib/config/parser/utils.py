import os.path
import typing

from schema import SchemaUnexpectedTypeError

from lib.config.validator import ProjectConfigValidator
from lib.helpers.filesystem import resolve_files, get_dirname, resolve_path, resolve_dirs, resolve_paths, join_path, \
    path_contains_filename
from lib.helpers.jsons import JSON
from lib.helpers.logging import Logger
from lib.helpers.object import clone_dict, clone_array
from lib.helpers.smart_merge import smart_merge
from lib.helpers.template import Template, TemplateUndefinedException
from lib.helpers.yamls import YAML


class ProjectConfigParserUtils:
    def get_base_config_names(self) -> typing.List[str]:
        return [
            "kubemize.yaml", ".kubemize.yaml",
            "kubemize.yml", ".kubemize.yml",
        ]

    def load_from_yaml(self, filename: str, cwd: str) -> dict:
        return YAML.from_file(filename=filename, cwd=cwd)

    def validate_config(self, config: dict, partial: bool = False) -> dict:
        return ProjectConfigValidator(partial).validate(config)

    def default_config(self, config: dict) -> dict:
        return ProjectConfigValidator(False).with_defaults(config)

    def load_and_validate_from_yaml(self, filename: str, cwd: str, partial: bool = False):
        try:
            return self.validate_config(config=self.load_from_yaml(filename=filename, cwd=cwd), partial=partial)
        except SchemaUnexpectedTypeError as ex:
            raise Exception(f"{resolve_path(filename, cwd=cwd)}: {str(ex)}")

    def resolve_paths(self, patterns: str or typing.List[str], cwd: str) -> typing.List[str]:
        # create array for paths
        paths = []
        # convert patterns to array
        patterns = patterns if isinstance(patterns, list) else [patterns]
        # resolve paths in pattern
        for pattern in patterns:
            if isinstance(pattern, str):
                resolved_paths = resolve_paths(pattern, cwd=cwd)
                if len(resolved_paths) > 0:
                    for path in resolved_paths:
                        paths.append(path)
                else:
                    Logger.warn("No dir(s) or file(s) found under '{0}'.".format(pattern))
        # return paths
        return paths

    def resolve_files(self, patterns: str or typing.List[str], cwd: str) -> typing.List[str]:
        # create array for files
        files = []
        # convert patterns to array
        patterns = patterns if isinstance(patterns, list) else [patterns]
        # resolve files in pattern
        for pattern in patterns:
            if isinstance(pattern, str):
                resolved_paths = resolve_files(pattern, cwd=cwd)
                if len(resolved_paths) > 0:
                    for path in resolved_paths:
                        files.append(path)
                else:
                    Logger.warn("No file(s) found under '{0}'.".format(pattern))
        # return files
        return files

    def resolve_dirs(self, patterns: str or typing.List[str], cwd: str) -> typing.List[str]:
        # create array for files
        dirs = []
        # convert patterns to array
        patterns = patterns if isinstance(patterns, list) else [patterns]
        # resolve files in pattern
        for pattern in patterns:
            if isinstance(pattern, str):
                resolved_paths = resolve_dirs(pattern, cwd=cwd)
                if len(resolved_paths) > 0:
                    for path in resolved_paths:
                        dirs.append(path)
                else:
                    Logger.warn("No dir(s) found under '{0}'.".format(pattern))
        # return files
        return dirs

    def resolve_path_patterns(self, items: str or dict or typing.List[str or dict], cwd: str) -> typing.List[dict]:
        # create array for paths
        paths = []
        # convert items to array
        items = items if isinstance(items, list) else [items]
        # check items
        for item in items:
            patterns = []
            if isinstance(item, dict) and "patterns" in item:
                patterns = item["patterns"]
            elif isinstance(item, str):
                patterns = item
            # resolve files
            for path in self.resolve_paths(patterns, cwd):
                if os.path.isfile(path):
                    paths.append({
                        "type": "file",
                        "path": path
                    })
                elif os.path.isdir(path):
                    paths.append({
                        "type": "dir",
                        "path": path
                    })
        # return paths
        return paths

    def resolve_file_patterns(self, items: str or dict or typing.List[str or dict], cwd: str) -> typing.List[str]:
        # create array for files
        files = []
        # convert items to array
        items = items if isinstance(items, list) else [items]
        # check items
        for item in items:
            patterns = []
            if isinstance(item, dict) and "patterns" in item:
                patterns = item["patterns"]
            elif isinstance(item, str):
                patterns = item
            # resolve files
            for file in self.resolve_files(patterns, cwd):
                files.append(file)
        # return files
        return files

    def resolve_dir_patterns(self, items: str or dict or typing.List[str or dict], cwd: str) -> typing.List[str]:
        # create array for dirs
        dirs = []
        # convert items to array
        items = items if isinstance(items, list) else [items]
        # check items
        for item in items:
            patterns = []
            if isinstance(item, dict) and "patterns" in item:
                patterns = item["patterns"]
            elif isinstance(item, str):
                patterns = item
            # resolve dirs
            for dir in self.resolve_dirs(patterns, cwd):
                dirs.append(dir)
        # return files
        return dirs

    def resolve_file(self, filename: str, cwd: str) -> str or None:
        return resolve_path(filename, cwd=cwd)

    def render_str_or_dict(self, obj: str or dict, variables: dict, source_file: str or None = None) -> str or dict:
        try:
            if isinstance(obj, str):
                return Template.render(obj, variables or {})
            elif isinstance(obj, dict):
                return Template.render_object(obj, variables or {})
            return obj
        except TemplateUndefinedException as ex:
            raise TemplateUndefinedException(message=ex.message, file=source_file)

    def parse_variables_from_arguments(self, variables_raw: typing.List[str]) -> dict:
        result: dict = {}
        for arg in variables_raw:
            key, value = arg.split('=', 1)
            keys = key.split('.')
            d = result
            for k in keys[:-1]:
                d = d.setdefault(k, {})
            d[keys[-1]] = value
        return result

    def render_variables(self, config: dict, variables: dict = None, global_variables: dict = None, source_file: str or None = None) -> dict:
        global_variables = clone_dict(global_variables or {})
        variables = clone_dict(variables or {})
        if "variables" in config and isinstance(config["variables"], dict):
            # merge variables with global variables
            variables_config = self.render_str_or_dict(
                obj=config["variables"],
                variables=smart_merge(variables, {"vars": global_variables}),
                source_file=source_file,
            )
            # merge variables with config variables
            variables_config = self.render_str_or_dict(
                obj=variables_config,
                variables=smart_merge(variables, {"vars": smart_merge(variables_config, global_variables)}),
                source_file=source_file,
            )
            # merge config variables into variables
            variables["vars"] = smart_merge(variables["vars"], smart_merge(variables_config, global_variables))
        return variables["vars"]

    def extract_configs(self, config: dict, config_path: str, cwd: str, variables: dict, global_config_path: str, global_config: dict = None, global_variables: dict = None) -> typing.List[dict]:
        # create array for configs
        configs: typing.List[dict] = []
        # set global config
        if not global_config:
            # render variables
            config["variables"] = self.render_variables(config, variables, global_variables, source_file=config_path)
            # overwrite variables
            variables["vars"] = smart_merge(variables["vars"], clone_dict(config["variables"]))
            # set global config
            global_config = config
            # add config to configs
            configs.append({
                "path": config_path,
                "cwd": cwd,
                "content": config,
            })
        # resolve all extends in config
        if JSON.isinstance("extends", list, config):
            # render patterns
            patterns = self.render_str_or_dict(config["extends"], variables, source_file=config_path)
            # resolve all files and dirs in pattern
            for config_path in self.resolve_path_patterns(patterns, cwd=cwd):
                # set config file
                config_file = config_path["path"]
                # skip if filename is "kubemize.yaml" or path of global config
                if config_path["type"] == "file":
                    if global_config_path == config_file or path_contains_filename(config_file, self.get_base_config_names()):
                        continue
                # check if type of file is dir
                if config_path["type"] == "dir":
                    for filename in self.get_base_config_names():
                        config_file = join_path(config_path["path"], filename)
                        if not os.path.exists(config_file) or not os.path.isfile(config_file):
                            config_file = None
                            continue
                        break
                    if not config_file:
                        Logger.warn(f"File '{join_path(config_path["path"], self.get_base_config_names()[0])}' does not exist or is no file.")
                        continue
                # load config
                config_base = self.load_and_validate_from_yaml(filename=config_file, cwd=cwd, partial=True)
                # render variables
                config_base["variables"] = self.render_variables(config_base, variables, global_variables=global_variables, source_file=config_file)
                # overwrite variables
                variables["vars"] = clone_dict(config_base["variables"])
                # get config cwd
                config_cwd = get_dirname(config_file, cwd=cwd)
                # add config to array
                configs.append({
                    "path": config_file,
                    "cwd": config_cwd,
                    "content": config_base,
                })
                # add nested config to array
                for child_config in self.extract_configs(config=config_base, config_path=config_file, cwd=config_cwd, variables=variables, global_config_path=global_config_path, global_config=global_config, global_variables=global_variables):
                    configs.append(child_config)
        # clone configs
        configs = clone_array(configs)
        # remove extends keys from configs
        for config in configs:
            if "extends" in config["content"]:
                del config["content"]["extends"]
        # return configs
        return configs

    def normalize_manifests(self, manifest) -> typing.List[dict]:
        # create array for manifests
        manifests = []
        if JSON.has_path_all_and_not_empty(["apiVersion", "kind"], manifest) and manifest["kind"].strip().lower() == "list":
            for item in JSON.get("items", manifest, []):
                for manifest in self.normalize_manifests(item):
                    manifests.append(manifest)
        else:
            manifests.append(manifest)
        # return manifests
        return manifests