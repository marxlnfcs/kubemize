import typing

from lib.helpers.jsons import JSON


class ProjectConfigHelmArgumentsSection:
    def __init__(self, data: dict, config):
        self.config = config
        self.data: dict = {}
        for key in (data if isinstance(data, dict) else {}):
            key_stripped = key.strip().lstrip("-")
            hyphen = self._count_hyphens(key)
            self.data[key_stripped] = {
                "key": ("-" * hyphen) + key_stripped,
                "value": data[key]
            }

    def get(self, path: str, fallback: any = None) -> any or None:
        return JSON.get(path.strip().lstrip("-"), self.data, fallback={"value": fallback})["value"]

    def has(self, path: str) -> bool:
        return JSON.has_path(path.strip().lstrip("-"), self.data)

    def get_first(self, paths: typing.List[str], fallback: any = None) -> any or None:
        for path in paths:
            value = self.get(path)
            if value is not None:
                return value
        return fallback

    def get_arguments(self) -> typing.List[{ "key": str, "value": any }]:
        items = []
        for key in self.data:
            items.append(self.data[key])
        return items

    def _count_hyphens(self, key: str):
        count = 0
        for char in key:
            if char == '-':
                count += 1
            else:
                break
        return count if count > 0 else 2

    def to_dict(self) -> dict:
        return self.data

class ProjectConfigHelmArguments:
    def __init__(self, data: dict, config):
        self.data: dict = data
        self.config = config

    def globally(self) -> ProjectConfigHelmArgumentsSection:
        return ProjectConfigHelmArgumentsSection(JSON.get("global", self.data, fallback={}), self.config)

    def apply(self) -> ProjectConfigHelmArgumentsSection:
        return ProjectConfigHelmArgumentsSection(JSON.get("apply", self.data, fallback={}), self.config)

    def destroy(self) -> ProjectConfigHelmArgumentsSection:
        return ProjectConfigHelmArgumentsSection(JSON.get("destroy", self.data, fallback={}), self.config)

    def to_dict(self) -> dict:
        return self.data