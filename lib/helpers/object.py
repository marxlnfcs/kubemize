import copy
import inspect
import typing


def is_primitive(obj: any) -> bool:
    if isinstance(obj, str):
        return True
    elif isinstance(obj, int):
        return True
    elif isinstance(obj, bool):
        return True
    elif isinstance(obj, float):
        return True
    else:
        return False

def is_iterable(obj: any) -> bool:
    return True if isinstance(obj, dict) or isinstance(obj, list) else False

def object_format_each_primitive(obj: any, formatter: typing.Callable) -> any:
    if not isinstance(obj, dict) and not isinstance(obj, list):
        return None

    for index in (obj.keys() if isinstance(obj, dict) else range(len(obj if isinstance(obj, list) else []))):
        item = obj[index]
        if is_primitive(item):
            res = formatter(item)
            if res is not None:
                obj[index] = res
        elif is_iterable(item):
            res = formatter(item)
            if res is not None:
                obj[index] = res
                item = res
            obj[index] = object_format_each_primitive(item, formatter)

    return obj

def to_dict(obj: any, custom_func: str = None) -> any:
    def formatter(value):
        if inspect.isclass(value.__class__):
            if not custom_func:
                if hasattr(value, "to_dict"):
                    return value.to_dict()
                elif hasattr(value, "to_json"):
                    return value.to_json()
            elif hasattr(value, custom_func):
                return value[custom_func]()
    return object_format_each_primitive(obj, formatter)

def flatten_array(*items) -> list:
    array = []
    for item in items:
        if isinstance(item, list):
            for sub_item in item:
                array.append(sub_item)
        else:
            array.append(item)
    return array

def clone_dict(obj: dict) -> dict:
    return copy.deepcopy(obj)

def clone_array(obj: list) -> list:
    return copy.deepcopy(obj)

def reverse_array(obj: list) -> list:
    return clone_array(obj)[::-1]