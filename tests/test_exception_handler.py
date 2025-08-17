from django.core import exceptions as django_exceptions
from django.http import Http404
from rest_framework import exceptions as drf_exceptions

import pytest

from drf_simple_api_errors.exception_handler import exception_handler
from tests.utils import render_response


class TestExceptionHandler:
    """
    Tests for the DRF exception handler response formatting
    for various exceptions.
    """

    @pytest.mark.parametrize(
        "error_message, code, params, expected_response",
        [
            # Raising a single error message
            (
                "Error message.",
                None,
                None,
                {
                    "title": "Validation error.",
                    "detail": ["Error message."],
                    "invalid_params": None,
                },
            ),
            (
                "Error message: %(msg)s.",
                "invalid",
                {"msg": "ERROR"},
                {
                    "title": "Validation error.",
                    "detail": ["Error message: ERROR."],
                    "invalid_params": None,
                },
            ),
            # Raising multiple error messages
            (
                [f"Error message {i+1}." for i in range(2)],
                None,
                None,
                {
                    "title": "Validation error.",
                    "detail": ["Error message 1.", "Error message 2."],
                    "invalid_params": None,
                },
            ),
            (
                [
                    django_exceptions.ValidationError(
                        f"Error message {i+1}.", code=f"error {i+1}"
                    )
                    for i in range(2)
                ],
                None,
                None,
                {
                    "title": "Validation error.",
                    "detail": ["Error message 1.", "Error message 2."],
                    "invalid_params": None,
                },
            ),
            # Raising a dictionary of error messages
            (
                {"field": "Error message."},
                None,
                None,
                {
                    "title": "Validation error.",
                    "detail": None,
                    "invalid_params": [{"name": "field", "reason": ["Error message."]}],
                },
            ),
            (
                {"field": [f"Error message {i+1}." for i in range(2)]},
                None,
                None,
                {
                    "title": "Validation error.",
                    "detail": None,
                    "invalid_params": [
                        {
                            "name": "field",
                            "reason": ["Error message 1.", "Error message 2."],
                        },
                    ],
                },
            ),
        ],
    )
    def test_django_validation_error(
        self, error_message, code, params, expected_response, mocker
    ):
        """
        Test the exception handler for can handle Django ValidationError
        exceptions and formats them into a structured API response.
        """
        exc = django_exceptions.ValidationError(error_message, code, params)
        response = exception_handler(exc, mocker.Mock())

        assert render_response(response.data) == expected_response

    def test_django_http404(self, mocker):
        """Test the exception handler for Http404 exceptions."""
        exc = Http404()
        response = exception_handler(exc, mocker.Mock())

        expected_response = {
            "title": "Not found.",
            "detail": None,
            "invalid_params": None,
        }
        assert render_response(response.data) == expected_response

    def test_django_permission_denied(self, mocker):
        """Test the exception handler for PermissionDenied exceptions."""
        exc = django_exceptions.PermissionDenied()
        response = exception_handler(exc, mocker.Mock())

        expected_response = {
            "title": "You do not have permission to perform this action.",
            "detail": None,
            "invalid_params": None,
        }
        assert render_response(response.data) == expected_response

    @pytest.mark.parametrize(
        "error_message, expected_response",
        [
            (
                "Error message.",
                {
                    "title": "A server error occurred.",
                    "detail": ["Error message."],
                    "invalid_params": None,
                },
            ),
            (
                [f"Error message {i}." for i in range(2)],
                {
                    "title": "A server error occurred.",
                    "detail": ["Error message 0.", "Error message 1."],
                    "invalid_params": None,
                },
            ),
            (
                {"field": "Error message."},
                {
                    "title": "A server error occurred.",
                    "detail": None,
                    "invalid_params": [{"name": "field", "reason": ["Error message."]}],
                },
            ),
            (
                {"field1": {"field2": "Error message."}},
                {
                    "title": "A server error occurred.",
                    "detail": None,
                    "invalid_params": [
                        {"name": "field1.field2", "reason": ["Error message."]}
                    ],
                },
            ),
        ],
    )
    def test_drf_api_exception(self, error_message, expected_response, mocker):
        exc = drf_exceptions.APIException(error_message)
        response = exception_handler(exc, mocker.Mock())

        assert render_response(response.data) == expected_response

    @pytest.mark.parametrize(
        "error_message, expected_response",
        [
            (
                "Error message.",
                {
                    "title": "Validation error.",
                    "detail": ["Error message."],
                    "invalid_params": None,
                },
            ),
            (
                [f"Error message {i}." for i in range(2)],
                {
                    "title": "Validation error.",
                    "detail": ["Error message 0.", "Error message 1."],
                    "invalid_params": None,
                },
            ),
            (
                {"field": "Error message."},
                {
                    "title": "Validation error.",
                    "detail": None,
                    "invalid_params": [{"name": "field", "reason": ["Error message."]}],
                },
            ),
            (
                {"field1": {"field2": "Error message."}},
                {
                    "title": "Validation error.",
                    "detail": None,
                    "invalid_params": [
                        {"name": "field1.field2", "reason": ["Error message."]}
                    ],
                },
            ),
            (
                {
                    "field1": {
                        "field2": {"field3": {"field4": {"field5": "Error message."}}}
                    }
                },
                {
                    "title": "Validation error.",
                    "detail": None,
                    "invalid_params": [
                        {
                            "name": "field1.field2.field3.field4.field5",
                            "reason": ["Error message."],
                        }
                    ],
                },
            ),
            (
                {
                    "field1": {"field2": "Error message."},
                    "field3": {"field4": "Error message."},
                },
                {
                    "title": "Validation error.",
                    "detail": None,
                    "invalid_params": [
                        {"name": "field1.field2", "reason": ["Error message."]},
                        {"name": "field3.field4", "reason": ["Error message."]},
                    ],
                },
            ),
            (
                {
                    "field1": {"field2": "Error message."},
                    "field3": {"field4": {"field5": "Error message."}},
                },
                {
                    "title": "Validation error.",
                    "detail": None,
                    "invalid_params": [
                        {"name": "field1.field2", "reason": ["Error message."]},
                        {"name": "field3.field4.field5", "reason": ["Error message."]},
                    ],
                },
            ),
        ],
    )
    def test_drf_validation_error(self, error_message, expected_response, mocker):
        exc = drf_exceptions.ValidationError(error_message)
        response = exception_handler(exc, mocker.Mock())

        assert render_response(response.data) == expected_response

    def test_drf_parser_error(self, mocker):
        """
        Test the exception handler for DRF ParserError exceptions.
        """
        exc = drf_exceptions.ParseError()
        response = exception_handler(exc, mocker.Mock())

        expected_response = {
            "title": "Malformed request.",
            "detail": None,
            "invalid_params": None,
        }
        assert render_response(response.data) == expected_response

    @pytest.mark.parametrize(
        "exception, expected_response",
        [
            (
                drf_exceptions.NotAuthenticated(),
                {
                    "title": "Authentication credentials were not provided.",
                    "detail": None,
                    "invalid_params": None,
                },
            ),
            (
                drf_exceptions.AuthenticationFailed(),
                {
                    "title": "Incorrect authentication credentials.",
                    "detail": None,
                    "invalid_params": None,
                },
            ),
        ],
    )
    def test_drf_authentication_exceptions(self, exception, expected_response, mocker):
        """
        Test the exception handler for DRF authentication exceptions.
        """
        response = exception_handler(exception, mocker.Mock())

        assert render_response(response.data) == expected_response

    def test_drf_permission_denied(self, mocker):
        """
        Test the exception handler for DRF PermissionDenied exceptions.
        """
        exc = drf_exceptions.PermissionDenied()
        response = exception_handler(exc, mocker.Mock())

        expected_response = {
            "title": "You do not have permission to perform this action.",
            "detail": None,
            "invalid_params": None,
        }
        assert render_response(response.data) == expected_response

    def test_drf_not_found(self, mocker):
        """
        Test the exception handler for DRF NotFound exceptions.
        """
        exc = drf_exceptions.NotFound()
        response = exception_handler(exc, mocker.Mock())

        expected_response = {
            "title": "Not found.",
            "detail": None,
            "invalid_params": None,
        }
        assert render_response(response.data) == expected_response

    def test_drf_method_not_allowed(self, mocker):
        """
        Test the exception handler for DRF MethodNotAllowed exceptions.
        """
        method = "GET"
        exc = drf_exceptions.MethodNotAllowed(method)
        response = exception_handler(exc, mocker.Mock())

        expected_response = {
            "title": "Method not allowed.",
            "detail": [f'Method "{method}" not allowed.'],
            "invalid_params": None,
        }
        assert render_response(response.data) == expected_response

    def test_drf_not_acceptable(self, mocker):
        """
        Test the exception handler for DRF NotAcceptable exceptions.
        """
        exc = drf_exceptions.NotAcceptable()
        response = exception_handler(exc, mocker.Mock())

        expected_response = {
            "title": "Could not satisfy the request Accept header.",
            "detail": None,
            "invalid_params": None,
        }
        assert render_response(response.data) == expected_response

    def test_drf_unsupported_media_type(self, mocker):
        """
        Test the exception handler for DRF UnsupportedMediaType exceptions.
        """
        media_type = "application/json"
        exc = drf_exceptions.UnsupportedMediaType(media_type)
        response = exception_handler(exc, mocker.Mock())

        expected_response = {
            "title": "Unsupported media type.",
            "detail": [f'Unsupported media type "{media_type}" in request.'],
            "invalid_params": None,
        }
        assert render_response(response.data) == expected_response

    @pytest.mark.parametrize(
        "wait, expected_detail",
        [
            (None, None),
            (1, ["Request was throttled. Expected available in 1 second."]),
            (60, ["Request was throttled. Expected available in 60 seconds."]),
        ],
    )
    def test_drf_throttled(self, mocker, wait, expected_detail):
        """
        Test the exception handler for DRF Throttled exceptions.
        """
        exc = drf_exceptions.Throttled(wait=wait)
        response = exception_handler(exc, mocker.Mock())

        expected_response = {
            "title": "Request was throttled.",
            "detail": expected_detail,
            "invalid_params": None,
        }
        assert render_response(response.data) == expected_response

    def test_unexpected_exception(self, mocker):
        """
        Test the exception handler for unexpected exceptions.
        This should return a 500 Internal Server Error response.
        """
        exc = Exception("Unexpected error")
        response = exception_handler(exc, mocker.Mock())
        assert response is None
