import logging
from typing import Dict, Union

from django.core.exceptions import (
    PermissionDenied,
    ValidationError as DjangoValidationError,
)
from django.http import Http404
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.views import set_rollback

from drf_simple_api_errors import formatter
from drf_simple_api_errors.exceptions import ServerError
from drf_simple_api_errors.settings import api_settings
from drf_simple_api_errors.types import ExceptionHandlerContext

logger = logging.getLogger(__name__)


def exception_handler(exc: Exception, context: ExceptionHandlerContext) -> Response:
    """
    Custom exception handler for DRF.

    This function handles exceptions and formats them into a structured API response,
    including Django exceptions. It also applies any extra handlers defined in the
    settings.

    The function will not handle exceptions that are not instances of or
    can be converted to DRF `APIException`.

    Args:
        exc (Exception): The exception raised.
        context (ExceptionHandlerContext): The context of the exception.

    Returns:
        Response: The formatted API response.
    """

    # This allows for custom exception handling logic.
    # If other kinds of exceptions are raised and should be handled,
    # they can be added to the EXTRA_HANDLERS setting.
    _apply_extra_handlers(exc)

    # If the exception is not an instance of APIException, we can try to convert it
    # to DRF APIException if it's a Django exception.
    exc = _convert_django_exc_to_drf_api_exc(exc)
    # If the exception is still not an instance of APIException, thus could be
    # converted to one, we cannot handle it.
    # This will result in a 500 error response without any detail.
    # This is because it's not good practice to expose the details of
    # unhandled exceptions to the client.
    if not isinstance(exc, exceptions.APIException):
        logger.debug("Server error", exc_info=True)
        return ServerError

    # Get the API response headers from the exception.
    headers = _get_response_headers(exc)
    # Get the API response data from the exception.
    # If the exception is an instance of APIException, we can handle it and
    # will format it to a structured API response data.
    data = formatter.format_exc(exc)
    # Set the rollback flag to True, if the transaction is atomic.
    set_rollback()
    # Finally, return the API response \(◕ ◡ ◕\)
    return Response(data, status=exc.status_code, headers=headers)


def _apply_extra_handlers(exc: Exception):
    """
    Apply any extra exception handlers defined in the settings.

    Args:
        exc (Exception): The exception to handle.
    """
    extra_handlers = api_settings.EXTRA_HANDLERS
    if extra_handlers:
        for handler in extra_handlers:
            handler(exc)


def _convert_django_exc_to_drf_api_exc(
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


def _get_response_headers(exc: exceptions.APIException) -> Dict:
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
