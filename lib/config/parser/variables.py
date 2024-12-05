import typing
from argparse import Namespace

from lib.config.parser.utils import ProjectConfigParserUtils
from lib.helpers.jsons import JSON
from lib.helpers.object import reverse_array
from lib.helpers.smart_merge import smart_merge


class ProjectConfigParserVariables:
    def __init__(self, arguments: Namespace):
        self.utils: ProjectConfigParserUtils = ProjectConfigParserUtils()
        self.global_variables: dict = self.utils.parse_variables_from_arguments(arguments.variables if "variables" in arguments else [])

    def parse(self, config: dict, config_file: str, cwd: str) -> dict:
        # create variables object with variables and locals
        variables = {
            "vars": {},
            "locals": {},
        }
        # extract all configs from config
        configs = self.utils.extract_configs(config, cwd=cwd, variables=variables, global_variables=self.global_variables, global_config_path=config_file, config_path=config_file)
        # get variables from configs
        variables["vars"] = self._merge_variables(configs, variables=variables, global_variables=self.global_variables)
        # get and parse locals from configs
        variables["locals"] = self._merge_locals(configs, variables=variables)
        # return variables
        return variables

    def _merge_variables(self, configs: typing.List[dict], variables: dict, global_variables: dict) -> dict:
        # reverse configs
        configs = reverse_array(configs)
        # merge variables
        for config_resource in configs:
            if JSON.isinstance("content.variables", dict, config_resource):
                variables["vars"] = smart_merge(variables["vars"], config_resource["content"]["variables"])
        # merge variables with global variables
        variables["vars"] = smart_merge(variables["vars"], global_variables)
        # return variables
        return variables["vars"]

    def _merge_locals(self, configs: typing.List[dict], variables: dict) -> dict:
        # merge locals
        for config_resource in configs:
            if JSON.isinstance("content.locals", dict, config_resource):
                variables["locals"] = smart_merge(config_resource["content"]["locals"], variables["locals"])
                variables["locals"] = smart_merge(variables["locals"], self.utils.render_str_or_dict(variables["locals"], variables=variables, source_file=config_resource["path"]))
        # return locals
        return variables["locals"]