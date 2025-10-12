"""
Handlers to deal with different types of exceptions and format them into
API error responses, and other utility functions.

Functions:
    - `apply_extra_handlers`:
        Applies any extra exception handlers defined in the settings.
    - `convert_django_exc_to_drf_api_exc`:
        Converts Django exceptions to DRF APIException, if possible.
    - `get_response_headers`: Gets the response headers for the given exception.
"""

import importlib
from typing import Callable, Dict, Union

from django.core.exceptions import (
    PermissionDenied,
    ValidationError as DjangoValidationError,
)
from django.http import Http404
from rest_framework import exceptions
from rest_framework.serializers import as_serializer_error

from drf_simple_api_errors import extra_handlers
from drf_simple_api_errors.settings import api_settings

DEFAULT_EXTRA_HANDLERS = [
    extra_handlers.set_default_detail_to_formatted_exc_default_code
]
"""Default extra handlers to always apply."""


def apply_extra_handlers(exc: Exception):
    """
    Apply any extra exception handlers defined in the settings.

    Args:
        exc (Exception): The exception to handle.

    Returns:
        int: The number of handlers applied (this is mainly for unit testing).
    """
    # Get the default extra handlers and the ones defined in the settings.
    # The default handlers are always applied to ensure that exceptions
    # are formatted correctly.
    # Resolve the settings extra handlers.
    # The settings extra handlers is a list of strings representing
    # the import path to the handler function.
    # This allows for lazy loading of the handlers.
    settings_extra_handlers: list[Callable] = []
    for handler_path in api_settings.EXTRA_HANDLERS or []:
        if not isinstance(handler_path, str):
            raise ValueError(
                f"EXTRA_HANDLERS must be a list of strings. Found: {type(handler_path)}"
            )

        module_path, func_name = handler_path.rsplit(".", 1)
        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError:
            raise ValueError(f"Path {handler_path} not found.")

        func = getattr(module, func_name, None)
        if func is None:
            raise ValueError(f"Handler {func_name} not found.")
        if not callable(func):
            raise ValueError(f"Handler {func_name} is not callable.")
        else:
            settings_extra_handlers.append(func)

    extra_handlers_to_apply = DEFAULT_EXTRA_HANDLERS + settings_extra_handlers
    if extra_handlers_to_apply:
        for handler in extra_handlers_to_apply:
            handler(exc)

    return len(extra_handlers_to_apply)


def convert_django_exc_to_drf_api_exc(
    exc: Exception,
) -> Union[exceptions.APIException, Exception]:
    """
    Convert Django exceptions to DRF APIException, if possible.

    Args:
        exc (Exception): The exception to convert.

    Returns:
        exceptions.APIException | Exception: The converted exception or the original.
    """
    if isinstance(exc, DjangoValidationError):
        return exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        return exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        return exceptions.PermissionDenied()

    return exc


def get_response_headers(exc: exceptions.APIException) -> Dict:
    """
    Get the response headers for the given exception.

    Args:
        exc (exceptions.APIException): The exception to get headers for.

    Returns:
        dict: A dictionary containing the response headers.
    """
    # This is from DRF's default exception handler.
    # https://github.com/encode/django-rest-framework/blob/48a21aa0eb3a95d32456c2a927eff9552a04231e/rest_framework/views.py#L87-L91
    headers = {}
    if getattr(exc, "auth_header", None):
        headers["WWW-Authenticate"] = exc.auth_header
    if getattr(exc, "wait", None):
        headers["Retry-After"] = "%d" % exc.wait

    return headers
