import json
import typing

from jsonpath_ng import parse as jsonpath_parse

from lib.helpers.filesystem import resolve_path, file_exists, write_file
from lib.helpers.object import to_dict, is_primitive


class JSON:
    @staticmethod
    def stringify(obj: any, indent: int = 0) -> str:
        return json.dumps(
            obj=to_dict(obj) if not is_primitive(obj) else obj,
            indent=indent if indent is not None and indent > 0 else None,
        )

    @staticmethod
    def parse(json_string: str) -> any:
        return json.loads(json_string)

    @staticmethod
    def to_file(filename: str, obj: any, indent: int = 0, cwd: str = None) -> any:
        write_file(
            path=filename,
            content=JSON.stringify(obj, indent),
            cwd=cwd,
        )
        return obj

    @staticmethod
    def from_file(filename: str, cwd: str = None, fallback: any = None) -> any:
        if file_exists(filename, cwd=cwd):
            with open(resolve_path(filename, cwd=cwd), "r") as file_handler:
                return JSON.parse(file_handler.read())
        return fallback or None


    @staticmethod
    def get_all(path: str, obj: any) -> typing.List[any]:
        if not isinstance(obj, dict) and not isinstance(obj, list):
            return []
        path = "$.{0}".format(path) if not path.startswith('$') else path
        expr = jsonpath_parse(path)
        return expr.find(obj)

    @staticmethod
    def has_path(path: str, obj: any) -> bool:
        return len(JSON.get_all(path, obj)) > 0

    @staticmethod
    def has_path_all(paths: typing.List[str], obj: any) -> bool:
        for path in paths:
            if not JSON.has_path(path, obj):
                return False
        return True

    @staticmethod
    def has_path_all_and_not_empty(paths: typing.List[str], obj: any) -> bool:
        for path in paths:
            if not JSON.has_path(path, obj) or not JSON.get(path, obj):
                return False
        return True

    @staticmethod
    def has_path_one(paths: typing.List[str], obj: any) -> bool:
        for path in paths:
            if JSON.has_path(path, obj):
                return True
        return False

    @staticmethod
    def get(path: str, obj: any, fallback: any or None = None) -> any or None:
        results = JSON.get_all(path, obj)
        return results[0].value if len(results) > 0 else fallback

    @staticmethod
    def get_first(paths: typing.List[str], obj: any, fallback: any or None = None) -> any or None:
        for path in paths:
            if JSON.has_path(path, obj):
                return JSON.get(path, obj, fallback)
        return fallback or None

    @staticmethod
    def isinstance(path: str, obj_type: any, obj: any) -> bool:
        return isinstance(JSON.get(path, obj), obj_type)