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

from typing import Dict, Union

from django.core.exceptions import (
    PermissionDenied,
    ValidationError as DjangoValidationError,
)
from django.http import Http404
from rest_framework import exceptions
from rest_framework.serializers import as_serializer_error

from drf_simple_api_errors import extra_handlers
from drf_simple_api_errors.settings import api_settings


def apply_extra_handlers(exc: Exception):
    """
    Apply any extra exception handlers defined in the settings.

    Args:
        exc (Exception): The exception to handle.
    """
    # Get the default extra handlers and the ones defined in the settings.
    # The default handlers are always applied to ensure that exceptions
    # are formatted correctly.
    default_extra_handlers = [
        extra_handlers.set_default_detail_to_formatted_exc_default_code
    ]
    settings_extra_handlers = api_settings.EXTRA_HANDLERS

    extra_handlers_to_apply = default_extra_handlers + settings_extra_handlers
    if extra_handlers_to_apply:
        for handler in extra_handlers_to_apply:
            handler(exc)


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
