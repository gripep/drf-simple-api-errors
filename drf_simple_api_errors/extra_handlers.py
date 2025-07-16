"""
This module contains custom error handlers for DRF exceptions.
It allows you to define additional handlers for specific exceptions
or to modify the behavior of existing exceptions.

Functions:
    - `set_default_detail_to_formatted_exc_default_code`:
        Formats the `default_detail` for specific DRF exceptions
        by setting it to a human-readable string based on the exception `default_code`.
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions


def set_default_detail_to_formatted_exc_default_code(
    exc: exceptions.APIException,
) -> exceptions.APIException:
    """
    Formats the `default_detail` for specific DRF exceptions
    by setting it to a human-readable string based on the exception `default_code`.

    This ensures that the `default_detail` is consistent and descriptive, such as
    'Method not allowed.' instead of using a template string, leaving the exception
    `detail` to be more informative.
    """
    exceptions_to_format = (
        exceptions.MethodNotAllowed,
        exceptions.UnsupportedMediaType,
    )

    if not isinstance(exc, exceptions_to_format):
        return exc

    # Compose the title based on the exception code.
    title = exc.default_code.replace("_", " ").capitalize() + "."
    exc.default_detail = _(title)
    return exc
