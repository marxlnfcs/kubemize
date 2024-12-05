import typing

from lib.config.schemes.helm_arguments import ProjectConfigHelmArguments
from lib.helpers.common import join_array
from lib.helpers.jsons import JSON

if typing.TYPE_CHECKING:
    from lib.config.config import ProjectConfig

class ProjectConfigHelmRelease:
    def __init__(self, data: dict, config: "ProjectConfig"):
        self.chart: dict = data
        self.config: "ProjectConfig" = config

    def is_oci(self) -> bool:
        return self.get_name().strip().lower().startswith("oci://")

    def get_identifier(self, include_namespace: bool = True, separator: str = None) -> str:
        separator = separator if separator else "/"
        return join_array(separator, self.get_namespace() if include_namespace else None, self.get_name()).strip().lower().replace("/", separator)

    def get_name(self) -> str:
        return self.chart["name"]

    def get_version(self) -> str or None:
        return self.chart["version"] if "version" in self.chart else None

    def get_namespace(self) -> str:
        if JSON.has_path("namespace", self.chart):
            return self.chart["namespace"]
        elif self.get_arguments().globally().has("namespace"):
            return self.get_arguments().globally().get("namespace")
        elif JSON.has_path("namespace", self.config.arguments):
            return JSON.get("namespace", self.config.arguments)
        else:
            return self.config.get_namespace()

    def get_chart(self) -> str:
        return self.chart["chart"]

    def get_repository_url(self) -> str or None:
        return JSON.get("repository", self.chart)

    def get_repository_username(self) -> str or None:
        return JSON.get("username", self.chart)

    def get_repository_password(self) -> str or None:
        return JSON.get("password", self.chart)

    def get_repository_pass_credentials(self) -> str or None:
        value = JSON.get("password", self.chart)
        if value is None and self.get_repository_username() and self.get_repository_password():
            return True
        else:
            return False

    def get_repository_ca_file(self) -> str or None:
        return JSON.get("caFile", self.chart)

    def get_repository_cert_file(self) -> str or None:
        return JSON.get("certFile", self.chart)

    def get_repository_key_file(self) -> str or None:
        return JSON.get("keyFile", self.chart)

    def get_repository_key_ring(self) -> str or None:
        return JSON.get("keyRing", self.chart)

    def get_repository_verify(self) -> str or None:
        return JSON.get("verify", self.chart)

    def get_arguments(self) -> ProjectConfigHelmArguments:
        return self.config.get_helm_arguments(self.chart)

    def get_set(self) -> dict:
        return JSON.get("set", self.chart, {})

    def set_values(self, values: dict) -> dict:
        self.chart["values"] = values
        return self.get_values()

    def get_values(self) -> any:
        return self.chart["values"] if "values" in self.chart else {}

    def to_dict(self) -> dict:
        return self.chart

    def to_state(self) -> dict:
        return {
            "name": self.get_name(),
            "namespace": self.get_namespace(),
            "chart": self.get_chart(),
            "set": self.get_set(),
            "values": self.get_values()
        }

    def to_info(self) -> dict:
        return {
            "name": self.get_name(),
            "namespace": self.get_namespace(),
            "chart": self.get_chart(),
            "repository": self.get_repository_url()
        }