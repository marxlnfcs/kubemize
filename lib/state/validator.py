from schema import Schema, SchemaError, Optional, Or


class ProjectStateValidator:
    def __init__(self):
        self.schema: Schema = self.__create_schema__()

    def __create_schema__(self) -> Schema:
        return Schema({
            Optional("charts", default={}): self.__create_charts_schema__(),
            Optional("manifests", default={}): self.__create_manifests_schema__(),
        })

    def __create_charts_schema__(self) -> Schema:
        return Schema({
            Optional(str): Schema({
                "name": str,
                "namespace": str,
                "chart": str,
                "set": {
                    Optional(str): Or(str, int, float, bool, dict, list)
                },
                "values": dict,
            })
        })

    def __create_manifests_schema__(self) -> Schema:
        return Schema({
            Optional(str): Schema({
                "apiVersion": str,
                "kind": str,
                "metadata": {
                    "name": str,
                    Optional("namespace"): str,
                    Optional(str): Or(str, int, float, bool, dict, list, Schema(None)),
                },
                Optional(str): Or(str, int, float, bool, dict, list, Schema(None))
            })
        })

    def validate(self, config: any) -> bool:
        try:
            self.schema.validate(config)
            return True
        except SchemaError as se:
            raise se

    def get_schema(self) -> dict:
        return self.schema.json_schema(self.schema.name)