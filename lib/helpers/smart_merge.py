import copy
import typing

from lib.helpers.jsons import JSON
from lib.helpers.object import is_primitive


def _is_mergeable(target: typing.Any, source: typing.Any):
    # return True if target is None or source is None
    if target is None or source is None:
        return True

    # return True if both have the same value
    if target == source:
        return True

    # return True if both are arrays
    if isinstance(target, list) and isinstance(source, list):
        return True

    # return True if both are dicts
    if isinstance(target, dict) and isinstance(source, dict):
        return True

    # return True if both are primitive types
    if isinstance(target, (str, bool, int, float)) and isinstance(source, (str, bool, int, float)):
        return True

    # otherwise, return False
    return False

def _has_all_keys(keys: typing.List[str], object_a: typing.Any, object_b: typing.Any) -> bool:
    return JSON.has_path_all_and_not_empty(keys, object_a) and JSON.has_path_all_and_not_empty(keys, object_b)

def _compare_keys(keys: typing.List[str], object_a: typing.Any, object_b: typing.Any) -> bool:
    if _has_all_keys(keys, object_a, object_b):
        for key in keys:
            value_a = JSON.get(key, object_a)
            value_b = JSON.get(key, object_b)
            if value_a != value_b:
                return False
        return True
    return False

def _find_similar_key(object_a: typing.Any, object_b: typing.Any):
    # prioritized keys
    # prioritized_keys = ["name", "path", "metadata.name"]
    prioritized_keys = [
        ["name", "namespace"],
        ["kind", "metadata.name", "metadata.namespace"],
        ["name"], ["path"],
    ]

    # check for prioritized keys
    for keys in prioritized_keys:
        if _has_all_keys(keys, object_a, object_b):
            return _compare_keys(keys, object_a, object_b)

    # check for prioritized keys
    # for key in prioritized_keys:
    #     if JSON.has_path(key, object_a) and JSON.has_path(key, object_b):
    #         value_a = JSON.get(key, object_a)
    #         value_b = JSON.get(key, object_b)
    #         if value_a == value_b:
    #             return True

    # check for similar keys
    for key in object_a:
        if is_primitive(object_a[key]) and is_primitive(object_b[key]):
            if object_a[key] == object_b[key]:
                return True

    # no result found
    return False


def _smart_merge_object(target: typing.Any, source: typing.Any):
    # create a deep copy of the target
    output = copy.deepcopy(target)

    # merge source into target
    for key, value in source.items():

        # skip if not mergeable or value is None
        if not _is_mergeable(output.get(key), value) or value is None:
            continue

        # merge arrays
        if isinstance(output.get(key), list):
            output[key] = smart_merge(output[key], value)
            continue

        # merge objects
        if isinstance(output.get(key), dict):
            output[key] = smart_merge(output[key], value)
            continue

        # merge primitive value into output
        output[key] = value

    return output


def _smart_merge_array(*items):
    output = []

    # process items
    for item_list in items:
        for item in item_list:

            # add to array if not an object nor array
            if not isinstance(item, (dict, list)):
                if item not in output:
                    output.append(item)
                continue

            # find similar item in the output
            similar_item_index = next((i for i, out_item in enumerate(output) if _find_similar_key(out_item, item)), -1)

            # merge item if similar item exists
            if similar_item_index != -1:
                output[similar_item_index] = smart_merge(output[similar_item_index], item)
            else:
                output.append(item)

    return output


def smart_merge(target: typing.Any, source: typing.Any):
    # return source if neither target nor source are objects or lists
    if not isinstance(target, (dict, list)) or not isinstance(source, (dict, list)):
        return source if target is None else target

    # return target if target and source are not of the same type
    if isinstance(target, list) != isinstance(source, list):
        return target

    # merge lists
    if isinstance(target, list):
        return _smart_merge_array(target, source)

    # merge objects (dictionaries in Python)
    return _smart_merge_object(target, source)