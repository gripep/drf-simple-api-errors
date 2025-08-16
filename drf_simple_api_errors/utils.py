"""
Utility functions for handling API errors and formatting responses.

Functions:
    - `camelize`:
        Converts a snake_case string to camelCase according to the CAMELIZE setting.
    - `flatten_dict`: Flattens a nested dictionary into a single-level dictionary
        according to the specified FIELDS_SEPARATOR setting.
"""

import re

from drf_simple_api_errors.settings import api_settings


def camelize(s: str) -> str:
    """
    Convert a snake_case string to camelCase according to
    the CAMELIZE setting (default to `False`).

    Args:
        s (str): The string to convert.
    Returns:
        str: The camelCase version of a string, or the original if CAMELIZE is `False`.
    """

    def underscore_to_camel(match: re.Match) -> str:
        group = match.group()
        if len(group) == 3:
            return group[0] + group[2].upper()
        else:
            return group

    if not api_settings.CAMELIZE:
        return s

    camelize_re = re.compile(r"[a-z0-9]?_[a-z0-9]")
    return re.sub(camelize_re, underscore_to_camel, s)


def flatten_dict(data: dict, parent_key: str = "") -> dict:
    """
    Flatten a nested dictionary into a single-level dictionary according to
    the specified FIELDS_SEPARATOR setting (default to `'.'`).

    Args:
        data (dict): The dictionary to flatten.
        parent_key (str):
            The base key to prepend to each key in the flattened dictionary.
            This is used for recursive calls to maintain the hierarchy.
    Returns:
        dict: A flattened dictionary with keys joined by the FIELDS_SEPARATOR.
    """
    sep = api_settings.FIELDS_SEPARATOR

    items: list = []
    for k, v in data.items():
        flat_k = sep.join([parent_key, k]) if parent_key and sep else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, flat_k).items())
        else:
            items.append((flat_k, v))

    return dict(items)
