from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class ServerError(APIException):
    """A class for REST framework '500 Internal Server' Error exception."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _("Server error.")
    default_code = "internal_server_error"
