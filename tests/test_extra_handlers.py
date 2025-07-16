from rest_framework import exceptions as drf_exceptions

import pytest

from drf_simple_api_errors import extra_handlers


class TestSetDefaultDetailHandler:
    """
    Test the set_default_detail_handler function from extra_handlers.
    Check this function sets the default detail of an exception to the formatted
    exception's default code.
    """

    @pytest.mark.parametrize(
        "exc, expected_default_detail",
        [
            (drf_exceptions.MethodNotAllowed("GET"), "Method not allowed."),
            (
                drf_exceptions.UnsupportedMediaType("application/json"),
                "Unsupported media type.",
            ),
        ],
    )
    def test_set_default_detail_correctly(self, exc, expected_default_detail):
        """
        Test that the handler sets the default detail to a human-readable string
        based on the exception's default code.
        """
        extra_handlers.set_default_detail_to_formatted_exc_default_code(exc)
        assert exc.default_detail == expected_default_detail
        assert exc.detail != expected_default_detail

    @pytest.mark.parametrize(
        "exc",
        [
            drf_exceptions.ValidationError("This is a validation error."),
            drf_exceptions.PermissionDenied(),
            drf_exceptions.NotFound(),
        ],
    )
    def test_set_default_detail_no_change_for_other_exceptions(self, exc):
        """
        Test that the handler does not change the default detail for exceptions
        that are not MethodNotAllowed or UnsupportedMediaType.
        """
        original_default_detail = exc.default_detail
        extra_handlers.set_default_detail_to_formatted_exc_default_code(exc)

        assert exc.default_detail == original_default_detail
