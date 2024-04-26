import re

from .settings import api_settings


def camelize(field: str) -> str:
    """Convert a snake_case string to camelCase."""

    def underscore_to_camel(match: re.Match) -> str:
        group = match.group()
        if len(group) == 3:
            return group[0] + group[2].upper()
        else:
            return group[1].upper()

    camelize_re = re.compile(r"[a-z0-9]?_[a-z0-9]")
    return re.sub(camelize_re, underscore_to_camel, field)


def flatten_dict(data: dict, parent_key: str = "") -> dict:
    """
    Flatten a nested dictionary into a single-level dictionary according to
    the specified FIELDS_SEPARATOR in your settings (default to '.').
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
