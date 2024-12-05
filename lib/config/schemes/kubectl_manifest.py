import typing

from lib.config.schemes.kubectl_arguments import ProjectConfigKubectlArguments
from lib.helpers.common import join_array
from lib.helpers.jsons import JSON

if typing.TYPE_CHECKING:
    from lib.config.config import ProjectConfig

class ProjectConfigKubectlManifest:
    def __init__(self, manifest: dict, config: "ProjectConfig"):
        self.manifest: dict = manifest
        self.config: "ProjectConfig" = config

    def get_identifier(self, include_namespace: bool = True, separator: str = None) -> str:
        separator = separator if separator else "/"
        return join_array(separator, self.get_kind(), join_array("_", self.get_namespace() if include_namespace else None, self.get_name().lower())).strip().replace("/", separator)

    def get_type(self) -> str:
        return join_array("/", self.get_api_version(), self.get_kind()).strip().lower()

    def get_api_version(self) -> str:
        return JSON.get("apiVersion", self.manifest)

    def get_kind(self) -> str:
        return JSON.get("kind", self.manifest)

    def get_name(self) -> str:
        return JSON.get("metadata.name", self.manifest)

    def get_namespace(self) -> str or None:
        return JSON.get("metadata.namespace", self.manifest)

    def get_content(self) -> dict:
        return self.manifest

    def get_arguments(self) -> ProjectConfigKubectlArguments:
        return self.config.get_kubectl_arguments()

    def to_dict(self) -> dict:
        return self.manifest

    def to_state(self) -> dict:
        return self.to_dict()

    def to_info(self) -> dict:
        return {
            "type": "/".join([self.get_api_version(), self.get_kind()]),
            "name": self.get_name(),
            "namespace": self.get_namespace(),
        }