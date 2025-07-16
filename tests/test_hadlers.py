from django.core import exceptions as django_exceptions
from django.http import Http404
from rest_framework import exceptions as drf_exceptions

import pytest

from drf_simple_api_errors import handlers


class TestApplyExtraHandlers:
    """Test cases for the apply_extra_handlers function in handlers module."""

    def test_extra_handlers_called(self, mocker):
        """
        Test that extra handlers are called with the exception.

        Testing with multiple handlers to ensure all are invoked, and this gives
        confidence one or more than two handlers can be used correctly.
        """
        mock_extra_handler = mocker.MagicMock()
        mock_another_extra_handler = mocker.MagicMock()

        mocker.patch(
            "drf_simple_api_errors.settings.api_settings.EXTRA_HANDLERS",
            [mock_extra_handler, mock_another_extra_handler],
        )

        exc = mocker.MagicMock()
        handlers.apply_extra_handlers(exc)

        mock_extra_handler.assert_called_once_with(exc)
        mock_another_extra_handler.assert_called_once_with(exc)

    def test_no_extra_handlers(self, mocker):
        """Test that no extra handlers are called when EXTRA_HANDLERS is empty."""
        mock_extra_handler = mocker.MagicMock()

        exc = mocker.MagicMock()
        handlers.apply_extra_handlers(exc)

        mock_extra_handler.assert_not_called()


class TestConvertDjangoExcToDRFAPIExc:
    """
    Test cases for the convert_django_exc_to_drf_api_exc function in handlers module.
    """

    def test_converts_django_validation_error(self):
        """
        Test that a Django ValidationError is converted to a DRF ValidationError.

        Trusting that rest_framework.serializers.as_serializer_error
        transfers the error message correctly, so
        not testing the content of the message.
        """
        exc = django_exceptions.ValidationError("Oh no, my spaghetti!")

        new_exc = handlers.convert_django_exc_to_drf_api_exc(exc)
        assert isinstance(new_exc, drf_exceptions.ValidationError)

    def test_converts_django_http404(self):
        """Test that a Django Http404 is converted to a DRF NotFound exception."""
        exc = Http404()

        new_exc = handlers.convert_django_exc_to_drf_api_exc(exc)
        assert isinstance(new_exc, drf_exceptions.NotFound)

    def test_converts_django_permission_denied(self):
        """
        Test that a Django PermissionDenied is converted to a DRF PermissionDenied.
        """
        exc = django_exceptions.PermissionDenied("No spaghetti for you!")

        new_exc = handlers.convert_django_exc_to_drf_api_exc(exc)
        assert isinstance(new_exc, drf_exceptions.PermissionDenied)

    def test_unknown_exception_not_converted(self):
        """
        Test that an unknown exception is not converted and remains the same type.
        This ensures that the function does not alter exceptions that
        are not recognized.
        """
        exc_class = Exception

        exc = exc_class()

        new_exc = handlers.convert_django_exc_to_drf_api_exc(exc)
        assert isinstance(new_exc, exc_class)


class TestGetResponseHeaders:
    """Test cases for the get_response_headers function in handlers module."""

    @pytest.mark.parametrize(
        "attr,value,header_name",
        [
            ("auth_header", "<challenge>", "WWW-Authenticate"),
            ("wait", 10, "Retry-After"),
        ],
    )
    def test_set_response_headers(self, mocker, attr, value, header_name):
        """
        Test that the response headers are set correctly based on
        the exception attributes.
        """
        exc = drf_exceptions.APIException("Spaghetti error")
        setattr(exc, attr, value)

        headers = handlers.get_response_headers(exc)

        assert headers[header_name] == str(value)

    def test_no_headers_when_no_attr(self):
        """
        Test that no headers are set when the exception does not have
        the relevant attributes.
        """
        exc = drf_exceptions.APIException("Spaghetti error")

        headers = handlers.get_response_headers(exc)

        assert not headers
