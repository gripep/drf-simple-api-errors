import logging

from django.core.exceptions import (
    PermissionDenied,
    ValidationError as DjangoValidationError,
)
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.views import set_rollback

from .handlers import exc_detail_handler, is_exc_detail_same_as_default_detail
from .settings import api_settings

logger = logging.getLogger(__name__)


def exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default this handles any REST framework `APIException`, and also
    Django's built-in `ValidationError`, `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions will log the exception message, and
    will cause a 500 error response.
    """

    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    extra_handlers = api_settings.EXTRA_HANDLERS
    if extra_handlers:
        for handler in extra_handlers:
            handler(exc)

    # unhandled exceptions, which should raise a 500 error and log the exception
    if not isinstance(exc, exceptions.APIException):
        logger.exception(exc)
        data = {"title": "Server error."}
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # from DRF
    # https://github.com/encode/django-rest-framework/blob/48a21aa0eb3a95d32456c2a927eff9552a04231e/rest_framework/views.py#L87-L91
    headers = {}
    if getattr(exc, "auth_header", None):
        headers["WWW-Authenticate"] = exc.auth_header
    if getattr(exc, "wait", None):
        headers["Retry-After"] = "%d" % exc.wait

    data = {}
    if isinstance(exc.detail, (list, dict)) and isinstance(
        exc, exceptions.ValidationError
    ):
        data["title"] = "Validation error."
        exc_detail_handler(data, exc.detail)
    else:
        data["title"] = exc.default_detail
        if not is_exc_detail_same_as_default_detail(exc):
            exc_detail_handler(
                data, [exc.detail] if isinstance(exc.detail, str) else exc.detail
            )

    set_rollback()
    return Response(data, status=exc.status_code, headers=headers)
