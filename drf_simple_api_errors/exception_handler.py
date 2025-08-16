import logging
from typing import Optional

from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import set_rollback

from drf_simple_api_errors import formatter, handlers
from drf_simple_api_errors.types import ExceptionHandlerContext

logger = logging.getLogger(__name__)


def exception_handler(
    exc: Exception, context: ExceptionHandlerContext
) -> Optional[Response]:
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
    handlers.apply_extra_handlers(exc)

    # If the exception is not an instance of APIException, we can try to convert it
    # to DRF APIException if it's a Django exception.
    exc = handlers.convert_django_exc_to_drf_api_exc(exc)
    # If the exception is still not an instance of APIException, thus could be
    # converted to one, we cannot handle it.
    # This will result in a 500 error response without any detail.
    # This is because it's not good practice to expose the details of
    # unhandled exceptions to the client.
    if not isinstance(exc, exceptions.APIException):
        return None

    # Get the API response headers from the exception.
    headers = handlers.get_response_headers(exc)
    # Get the API response data from the exception.
    # If the exception is an instance of APIException, we can handle it and
    # will format it to a structured API response data.
    data = formatter.format_exc(exc)
    # Set the rollback flag to True, if the transaction is atomic.
    set_rollback()
    # Finally, return the API response \(◕ ◡ ◕\)
    return Response(data, status=exc.status_code, headers=headers)
