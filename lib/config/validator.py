from schema import Schema, SchemaError, Optional, Or

from lib.helpers.smart_merge import smart_merge


class ProjectConfigValidator:
    def __init__(self, partial: bool):
        self.schema: Schema = self._create_schema(partial)

    def _create_schema(self, partial: bool) -> Schema:
        return Schema({
            Optional("extends"): self._create_file_patterns_schema(partial),
            Optional("hooks"): self._create_hooks_schema(partial),
            Optional("namespace"): str,
            Optional("helm"): self._create_helm_schema(partial),
            Optional("kubectl"): self._create_kubectl_schema(partial),
            Optional("locals"): dict,
            Optional("variables"): dict,
        }, ignore_extra_keys=False)

    def _create_file_patterns_schema(self, partial: bool) -> Schema:
        return Schema([Or(
            Schema(str),
            Schema({
                "patterns": [str]
            })
        )])

    def _create_arguments_schema(self, partial: bool) -> Schema:
        return Schema({
            Optional("global"): self._create_arguments_section_schema(partial),
            Optional("apply"): self._create_arguments_section_schema(partial),
            Optional("destroy"): self._create_arguments_section_schema(partial),
        })

    def _create_arguments_section_schema(self, partial: bool) -> Schema:
        return Schema({
            Optional(str): Or(str, int, bool, float, dict, Schema(None), Schema([Or(str, int, bool, float, Schema(None))])),
        })

    def _create_helm_schema(self, partial: bool) -> Schema:
        return Schema({
            Optional("arguments"): self._create_arguments_schema(partial),
            Optional("repositories"): self._create_helm_repositories_schema(partial),
            Optional("releases"): self._create_helm_releases_schema(partial),
        })

    def _create_helm_repositories_schema(self, partial: bool) -> Schema:
        return Schema([{
            (Optional("name") if partial else "name"): str,
            (Optional("url") if partial else "url"): str,
            Optional("username"): str,
            Optional("password"): str,
            Optional("passCredentials"): bool,
            Optional("certFile"): str,
            Optional("keyFile"): str,
            Optional("keyRing"): str,
            Optional("verify"): bool,
        }])

    def _create_helm_releases_schema(self, partial: bool) -> Schema:
        return Schema([{
            (Optional("name") if partial else "name"): str,
            (Optional("chart") if partial else "chart"): str,
            Optional("arguments"): self._create_arguments_schema(partial),
            Optional("version"): str,
            Optional("namespace"): str,
            Optional("values"): Schema(self._create_file_patterns_schema(partial)),
            Optional("set"): {
                Optional(str): Or(
                    str,
                    Schema({"type": "file", "path": str}),
                    Schema({"type": "json", "data": dict or list}),
                    Schema({"type": "literal", "value": str}),
                    Schema({"type": "string", "value": str}),
                )
            },
            Optional("repository"): str,
            Optional("username"): str,
            Optional("password"): str,
            Optional("passCredentials"): bool,
            Optional("caFile"): str,
            Optional("certFile"): str,
            Optional("keyFile"): str,
            Optional("keyRing"): str,
            Optional("verify"): bool,
        }])

    def _create_kubectl_schema(self, partial: bool) -> Schema:
        return Schema({
            Optional("order"): [str],
            Optional("arguments", {}): self._create_arguments_schema(partial),
            Optional("manifests"): self._create_file_patterns_schema(partial),
            Optional("generators", {}): Schema({
                Optional("configMaps"): self._create_kubectl_generators_configmaps_schema(partial),
                Optional("secrets"): self._create_kubectl_generators_secrets_schema(partial),
            })
        })

    def _create_kubectl_generators_configmaps_schema(self, partial: bool) -> Schema:
        return Schema([{
            "name": str,
            Optional("namespace"): str,
            Optional("annotations"): dict,
            Optional("labels"): dict,
            Optional("data"): self._create_kubectl_generators_configmaps_item_schema(partial),
        }])

    def _create_kubectl_generators_configmaps_item_schema(self, partial: bool) -> Schema:
        return Schema({
            Optional(str): Or(
                str, int, float, bool,
                Schema({"value": Or(str, int, float, bool)}),
                Schema({"type": "file", "path": str}),
                Schema({"type": "json", "value": Or(dict, list)}),
                Schema({"type": "yaml", "value": Or(dict, list)}),
            )
        })

    def _create_kubectl_generators_secrets_schema(self, partial: bool) -> Schema:
        return Schema([{
            "name": str,
            Optional("namespace"): str,
            Optional("annotations"): dict,
            Optional("labels"): dict,
            Optional("data"): self._create_kubectl_generators_configmaps_item_schema(partial),
            Optional("type"): str,
        }])

    def _create_kubectl_generators_secrets_item_schema(self, partial: bool) -> Schema:
        return Schema({
            Optional(str): Or(
                str, int, float, bool,
                Schema({"value": Or(str, int, float, bool)}),
                Schema({"type": "base64", "value": str}),
                Schema({"type": "file", "path": str}),
                Schema({"type": "json", "value": Or(dict, list)}),
                Schema({"type": "yaml", "value": Or(dict, list)}),
            )
        })

    def _create_hooks_schema(self, partial: bool) -> Schema:
        return Schema({
            Optional("pre_all"): self._create_file_patterns_schema(partial),
            Optional("post_all"): self._create_file_patterns_schema(partial),
            Optional("pre_apply"): self._create_file_patterns_schema(partial),
            Optional("post_apply"): self._create_file_patterns_schema(partial),
            Optional("pre_template"): self._create_file_patterns_schema(partial),
            Optional("post_template"): self._create_file_patterns_schema(partial),
            Optional("pre_standalone"): self._create_file_patterns_schema(partial),
            Optional("post_standalone"): self._create_file_patterns_schema(partial),
            Optional("pre_plan"): self._create_file_patterns_schema(partial),
            Optional("post_plan"): self._create_file_patterns_schema(partial),
            Optional("pre_destroy"): self._create_file_patterns_schema(partial),
            Optional("post_destroy"): self._create_file_patterns_schema(partial),
        })

    def validate(self, config: any) -> dict:
        try:
            return smart_merge(self.get_defaults(), self.schema.validate(config))
        except SchemaError as se:
            raise se

    def with_defaults(self, config: any) -> dict:
        return smart_merge(self.get_defaults(), config)

    def get_defaults(self) -> dict:
        return {
            "extends": [],
            "hooks": {
                "pre_all": [],
                "post_all": [],
                "pre_apply": [],
                "post_apply": [],
                "pre_template": [],
                "post_template": [],
                "pre_standalone": [],
                "post_standalone": [],
                "pre_plan": [],
                "post_plan": [],
                "pre_destroy": [],
                "post_destroy": [],
            },
            "helm": {
                "arguments": {
                    "global": {},
                    "apply": {},
                    "destroy": {}
                },
                "repositories": [],
                "releases": [],
            },
            "kubectl": {
                "order": [],
                "manifests": [],
                "generators": {
                    "configMaps": [],
                    "secrets": [],
                }
            }
        }

    def get_schema(self) -> dict:
        return self.schema.json_schema(self.schema.name)