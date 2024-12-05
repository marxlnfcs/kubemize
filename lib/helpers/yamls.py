import yaml

from lib.helpers.filesystem import resolve_path, file_exists, write_file
from lib.helpers.object import is_primitive, object_format_each_primitive


class YAMLQuoted(str): pass
class YAMLMultiline(str): pass

def YAMLQuotedRepresenter(dumper, data): return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')
def YAMLMultilineRepresenter(dumper, data): return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(YAMLQuoted, YAMLQuotedRepresenter)
yaml.add_representer(YAMLMultiline, YAMLMultilineRepresenter)


class YAML:
    @staticmethod
    def stringify(obj: any) -> str:
        if isinstance(obj, list):
            return yaml.dump_all(
                documents=YAML._pre_stringify(obj),
                sort_keys=False,
                default_flow_style=False,
            )
        return yaml.dump(
            data=YAML._pre_stringify(obj),
            sort_keys=False,
            default_flow_style=False,
        )

    @staticmethod
    def _pre_stringify(obj: any) -> any:
        if is_primitive(obj):
           return obj
        def _formatter(value: any):
            if isinstance(value, str) and not isinstance(value, YAMLQuoted) and not isinstance(value, YAMLMultiline):
                if len(value.split('\n')) > 1:
                    return YAMLMultiline(value)
                return YAMLQuoted(value)
            return value

        return object_format_each_primitive(obj, _formatter)


    @staticmethod
    def parse(yaml_string: str) -> any:
        return yaml.safe_load(yaml_string)

    @staticmethod
    def parse_all(yaml_string: str) -> any:
        return yaml.safe_load_all(yaml_string)

    @staticmethod
    def to_file(filename: str, obj: any, cwd: str = None) -> any:
        write_file(
            path=filename,
            content=YAML.stringify(obj),
            cwd=cwd,
        )
        return obj

    @staticmethod
    def from_file(filename: str, cwd: str = None, fallback: any = None) -> any:
        if file_exists(filename, cwd=cwd):
            with open(resolve_path(filename, cwd=cwd), "r") as file_handler:
                return YAML.parse(file_handler.read())
        return fallback or None
