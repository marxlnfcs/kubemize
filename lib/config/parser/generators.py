import base64
import typing

from lib.config.parser.utils import ProjectConfigParserUtils
from lib.helpers.filesystem import read_file
from lib.helpers.jsons import JSON
from lib.helpers.yamls import YAML


class ProjectConfigParserGenerators:
    def __init__(self):
        self.utils: ProjectConfigParserUtils = ProjectConfigParserUtils()

    def generate_configmaps(self, config: dict, variables: dict) -> typing.List[dict]:
        items = []
        for item in config["kubectl"]["generators"]["configMaps"]:
            items.append(self._generate_configmap(item, variables))
        return items

    def generate_secrets(self, config: dict, variables: dict) -> typing.List[dict]:
        items = []
        for item in config["kubectl"]["generators"]["secrets"]:
            items.append(self._generate_secret(item, variables))
        return items

    def _generate_configmap(self, item: dict, variables: dict) -> dict:
        # create empty manifest
        manifest = self._generate_manifest(
            api_version="v1",
            kind="ConfigMap",
            name=item["name"],
            namespace=item["namespace"] if "namespace" in item else None,
        )
        # create data
        manifest["data"] = self._create_data(
            data_dict=item["data"] if "data" in item else {},
            variables=variables,
            encode_base64=False
        )
        # return manifest
        return manifest
    def _generate_secret(self, item: dict, variables: dict) -> dict:
        # create empty manifest
        manifest = self._generate_manifest(
            api_version="v1",
            kind="Secret",
            name=item["name"],
            namespace=item["namespace"] if "namespace" in item else None,
            type=item["type"] if "type" in item else "Opaque",
        )
        # create data
        manifest["data"] = self._create_data(
            data_dict=item["data"] if "data" in item else {},
            variables=variables,
            encode_base64=True
        )
        # return manifest
        return manifest

    def _generate_manifest(self, api_version: str, kind: str, name: str, namespace: str, **kwargs) -> dict:
        return {
            "apiVersion": api_version,
            "kind": kind,
            "metadata": {
                "name": name,
                "namespace": namespace,
                "annotations": {},
                "labels": {},
            },
            **kwargs,
        }

    def _create_data(self, data_dict: dict, variables: dict, encode_base64: bool) -> dict:
        data = {}
        for key in data_dict:
            # extract item from data dict
            item = data_dict[key]
            # add data base64 encoded to data if primitive
            if isinstance(item, str) or isinstance(item, int) or isinstance(item, float) or isinstance(item, bool) or (isinstance(item, dict) and "type" not in item and "value" in item):
                data[key] = self._create_data_content(data=self.utils.render_str_or_dict(obj=item["value"] if isinstance(item, dict) else item, variables=variables), encode_base64=encode_base64)
            elif "type" in item and item["type"] == "base64":
                data[key] = item["value"]
            elif "type" in item and item["type"] == "json":
                data[key] = self._create_data_content(data=JSON.stringify(self.utils.render_str_or_dict(item["value"], variables=variables), 2), encode_base64=encode_base64)
            elif "type" in item and item["type"] == "yaml":
                data[key] = self._create_data_content(data=YAML.stringify(self.utils.render_str_or_dict(item["value"], variables=variables)), encode_base64=encode_base64)
            elif "type" in item and item["type"] == "file":
                data[key] = self._create_data_content(data=self.utils.render_str_or_dict(read_file(item["path"]), variables), encode_base64=encode_base64)
        return data

    def _create_data_content(self, data: any, encode_base64: bool) -> str:
        if isinstance(data, int) or isinstance(data, float):
            data = str(data)
        elif isinstance(data, bool):
            data = "true" if data else "false"
        return base64.b64encode(bytes(data, 'utf-8')).decode('utf-8') if encode_base64 else data