import copy
import os
import typing
from argparse import Namespace

from .parser.parser import ProjectConfigParser
from .schemes.helm_arguments import ProjectConfigHelmArguments
from .schemes.helm_release import ProjectConfigHelmRelease
from .schemes.helm_repository import ProjectConfigHelmRepository
from .schemes.kubectl_arguments import ProjectConfigKubectlArguments
from .schemes.kubectl_manifest import ProjectConfigKubectlManifest
from ..helpers.filesystem import resolve_path
from ..helpers.jsons import JSON
from ..helpers.smart_merge import smart_merge


class ProjectConfig:
    def __init__(self, project_dir: str, project_config: str, arguments: Namespace):
        # create parser
        self.parser: ProjectConfigParser = ProjectConfigParser(project_dir, project_config, arguments)
        # parse config
        self.config: dict = self.parser.parse()
        # set arguments
        self.arguments: Namespace = arguments

    def get_namespace(self) -> str:
        return self.config["namespace"] if "namespace" in self.config else "default"

    def get_helm(self) -> dict:
        return self.config["helm"] if "helm" in self.config else {}

    def get_helm_arguments(self, release: dict = None) -> ProjectConfigHelmArguments:
        return ProjectConfigHelmArguments({
            "global": smart_merge(JSON.get("arguments.global", self.get_helm(), {}), JSON.get("arguments.global", release, {})),
            "apply": smart_merge(JSON.get("arguments.apply", self.get_helm(), {}), JSON.get("arguments.apply", release, {})),
            "destroy": smart_merge(JSON.get("arguments.destroy", self.get_helm(), {}), JSON.get("arguments.destroy", release, {})),
        }, self)

    def get_helm_repositories(self) -> typing.List[ProjectConfigHelmRepository]:
        items = []
        for item in (self.get_helm()["repositories"] if "repositories" in self.get_helm() else []):
            items.append(ProjectConfigHelmRepository(item, self))
        return items

    def get_repository_by_chart_name(self, name: str) -> ProjectConfigHelmRepository:
        chart_parts = name.split('/')
        chart_parts.pop()
        if len(chart_parts) == 0:
            raise TypeError("No repository for chart '{0}' found.".format(name))
        repository: ProjectConfigHelmRepository = None
        repository_name = "/".join(chart_parts).strip().lower()
        for repo in self.get_helm_repositories():
            if repo.get_name().strip().lower() == repository_name:
                repository = repo
        if not repository:
            raise TypeError("Repository '{0}' not found.".format(repository_name))
        return repository

    def get_helm_releases(self) -> typing.List[ProjectConfigHelmRelease]:
        items = []
        for item in (self.get_helm()["releases"] if "releases" in self.get_helm() else []):
            item = copy.copy(item)
            if not item["chart"].strip().lower().startswith("oci://") and not JSON.get("repository", item):
                repository = self.get_repository_by_chart_name(item["chart"])
                item["chart"] = item["chart"].split("/").pop()
                item["repository"] = JSON.get("repository", item, fallback=repository.get_url())
                item["username"] = JSON.get("username", item, fallback=repository.get_username())
                item["password"] = JSON.get("password", item, fallback=repository.get_password())
                item["passCredentials"] = JSON.get("passCredentials", item, fallback=repository.pass_credentials())
                item["certFile"] = JSON.get("certFile", item, fallback=repository.get_cert_file())
                item["keyFile"] = JSON.get("keyFile", item, fallback=repository.get_key_file())
                item["keyRing"] = JSON.get("keyRing", item, fallback=repository.get_key_ring())
                item["verify"] = JSON.get("verify", item, fallback=repository.get_verify())
            items.append(ProjectConfigHelmRelease(item, self))
        return items

    def get_kubectl(self) -> dict:
        return self.config["kubectl"] if "kubectl" in self.config else {}

    def get_kubectl_arguments(self) -> ProjectConfigKubectlArguments:
        return ProjectConfigKubectlArguments({
            "global": JSON.get("arguments.global", self.get_kubectl(), {}),
            "apply": JSON.get("arguments.apply", self.get_kubectl(), {}),
            "destroy": JSON.get("arguments.destroy", self.get_kubectl(), {}),
        }, self)

    def get_kubectl_order(self) -> typing.List[str]:
        order = []
        order_config = self.get_kubectl()["order"] if "order" in self.get_kubectl() else []
        order_defaults = {
            "namespace": ["namespace", "v1/namespace"],
            "service": ["service", "v1/service"]
        }
        for key in order_defaults:
            found = False
            for default_type in order_defaults[key]:
                default_type = default_type.strip().lower()
                for order_type in order_config:
                    order_type = order_type.strip().lower()
                    if default_type == order_type:
                        found = True
            if not found:
                order.append(key.strip().lower())
        for key in order_config:
            order.append(key.strip().lower())
        return order

    def get_kubectl_manifests(self) -> typing.List[ProjectConfigKubectlManifest]:
        items = []
        for item in JSON.get("manifests", self.get_kubectl(), []):
            items.append(ProjectConfigKubectlManifest(item, self))
        return items

    def get_locals(self) -> dict:
        return self.config["locals"] if "locals" in self.config else {}

    def get_variables(self) -> dict:
        return self.config["variables"] if "variables" in self.config else {}

    def get_output_dir(self) -> str:
        return self.arguments.output if "output" in self.arguments else resolve_path(".tmp", cwd=os.getcwd())

    def ignore_not_found(self) -> bool:
        return self.arguments.ignore_not_found if "ignore_not_found" in self.arguments else False

    def get_helm_executable(self) -> str:
        return self.arguments.helm_executable if "helm_executable" in self.arguments else "helm"

    def get_hooks_pre_all(self) -> typing.List[str]:
        return JSON.get("hooks.pre_all", self.config, [])

    def get_hooks_post_all(self) -> typing.List[str]:
        return JSON.get("hooks.post_all", self.config, [])

    def get_hooks_pre_apply(self) -> typing.List[str]:
        return JSON.get("hooks.pre_apply", self.config, [])

    def get_hooks_post_apply(self) -> typing.List[str]:
        return JSON.get("hooks.post_apply", self.config, [])

    def get_hooks_pre_template(self) -> typing.List[str]:
        return JSON.get("hooks.pre_template", self.config, [])

    def get_hooks_post_template(self) -> typing.List[str]:
        return JSON.get("hooks.post_template", self.config, [])

    def get_hooks_pre_standalone(self) -> typing.List[str]:
        return JSON.get("hooks.pre_standalone", self.config, [])

    def get_hooks_post_standalone(self) -> typing.List[str]:
        return JSON.get("hooks.post_standalone", self.config, [])

    def get_hooks_pre_plan(self) -> typing.List[str]:
        return JSON.get("hooks.pre_plan", self.config, [])

    def get_hooks_post_plan(self) -> typing.List[str]:
        return JSON.get("hooks.post_plan", self.config, [])

    def get_hooks_pre_destroy(self) -> typing.List[str]:
        return JSON.get("hooks.pre_destroy", self.config, [])

    def get_hooks_post_destroy(self) -> typing.List[str]:
        return JSON.get("hooks.post_destroy", self.config, [])

    def get_kubectl_executable(self) -> str:
        return self.arguments.kubectl_executable if "kubectl_executable" in self.arguments else "kubectl"

    def get_kube_config(self) -> str or None:
        return self.arguments.kube_config if "kube_config" in self.arguments else None

    def get_kube_context(self) -> str or None:
        return self.arguments.kube_context if "kube_context" in self.arguments else None

    def get_kube_insecure(self) -> str or None:
        return self.arguments.kube_insecure if "kube_insecure" in self.arguments else False

    def to_dict(self) -> dict:
        return self.config
