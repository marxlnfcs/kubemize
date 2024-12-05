import typing

from jinja2 import Template as JinjaTemplate, Undefined, StrictUndefined, UndefinedError
from jinja2.utils import missing, object_type_repr

from lib.helpers.filesystem import file_exists
from lib.helpers.object import object_format_each_primitive
from lib.helpers.yamls import YAML


class ExtendedUndefined(StrictUndefined):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def _undefined_message(self) -> str:
        if self._undefined_hint or self._undefined_obj is missing or not self._get_vars_info_path(self._undefined_obj):
            return super()._undefined_message
        path = self._get_vars_info_path(self._undefined_obj)
        return "'{0}' of type '{1}' has no {2} '{3}'".format(
            path,  # path of the object
            object_type_repr(self._undefined_obj),  # type of the object
            "attribute" if isinstance(self._undefined_name, str) else "element",
            self._undefined_name,
        )

    def _get_vars_info_path(self, obj: any) -> str or None:
        for key in self._get_vars_info:
            if self._get_vars_info[key] == obj:
                return key
        return None

    @property
    def _get_vars_info(self) -> dict:
        return globals()['TemplateVarsInfo'] if "TemplateVarsInfo" in globals() else {}

class TemplateUndefinedException(Exception):
    def __init__(self, message: str, file: str = None):
        self.message = " ".join([message, f"in '{file}'"]) if file and file not in message else message
        super().__init__(self.message)

def _create_vars_info(obj: any, info: dict = None, parent: str = None) -> dict:
    if info is None:
        info = {}
    if not isinstance(obj, dict) and not isinstance(obj, list):
        return info
    elif isinstance(obj, dict):
        for key in obj:
            path = "{0}.{1}".format(parent, key) if parent else key
            info[path] = obj[key]
            _create_vars_info(obj[key], info, path)
    elif isinstance(obj, list):
        for index in range(len(obj)):
            path = "{0}[{1}]".format(parent, index) if parent else "[{0}]".format(index)
            info[path] = obj[index]
            _create_vars_info(obj[index], info, path)
    # return info
    return info

class Template:
    @staticmethod
    def _get_template(content: str, undefined: typing.Type[Undefined] = ExtendedUndefined) -> JinjaTemplate:
        return JinjaTemplate(source=content, undefined=undefined)

    @staticmethod
    def render(content: str, data: dict = None) -> str:
        try:
            # create variables
            data = data or {}
            # convert variables to dot-notation
            globals()['TemplateVarsInfo'] = _create_vars_info(data)
            # render template
            return Template._get_template(content).render(data)
        except UndefinedError as ex:
            raise TemplateUndefinedException(message=ex.message)

    @staticmethod
    def render_object(content: str or dict, data: dict = None) -> any:
        if isinstance(content, str):
            return Template.render(content, data)
        else:
            def formatter(c: any):
                if isinstance(c, str):
                    return Template.render(c, data)
                return None
            return object_format_each_primitive(content, formatter)

    @staticmethod
    def render_file(file: str, data: dict = None) -> str or None:
        try:
            if file_exists(file):
                with open(file, "r") as f:
                    return Template.render(f.read(), data)
            return None
        except TemplateUndefinedException as ex:
            raise TemplateUndefinedException(message=ex.message, file=file)

    @staticmethod
    def render_and_parse_yaml(file: str, data: dict = None) -> dict or None:
        content = Template.render_file(file, data)
        return YAML.parse(content) if content is not None else None

    @staticmethod
    def render_and_parse_all_yaml(file: str, data: dict = None) -> typing.List[dict]:
        content = Template.render_file(file, data)
        items = []
        for item in (YAML.parse_all(content) if content is not None else []):
            items.append(item)
        return items
