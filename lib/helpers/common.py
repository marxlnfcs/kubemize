import hashlib

from lib.helpers.jsons import JSON


def parse_boolean(o: str | bool) -> bool:
    if isinstance(o, bool):
        return o
    elif isinstance(o, str):
        return o.lower() in ['true', '1', 't', 'y', 'yes']


def to_md5(o: str or dict or list) -> str:
    data: str = ""
    if isinstance(o, str):
        data = o
    elif isinstance(o, dict) or isinstance(o, list):
        data = JSON.stringify(o)
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def join_array(separator: str, *array: str or None) -> str:
    items = []
    for item in array:
        if item is not None:
            items.append(item)
    return separator.join(items)
