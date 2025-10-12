import importlib
import types

from django.core import exceptions as django_exceptions
from django.http import Http404
from rest_framework import exceptions as drf_exceptions

import pytest

from drf_simple_api_errors import handlers


class TestApplyExtraHandlers:
    """Test cases for the apply_extra_handlers function in handlers module."""

    @pytest.fixture
    def mock_importlib_import_module(self, mocker):
        """Mock importlib.import_module to control the import behavior in tests."""
        return mocker.patch.object(importlib, "import_module")

    def test_calls_expected_default_handlers(self, mocker):
        """Test that all the expected default handlers are called.

        This is a sanity check to ensure that the default handlers are always called.
        """
        # Always make sure that the settings handlers are empty for this test
        # to isolate the default handlers.
        mocker.patch("drf_simple_api_errors.settings.api_settings.EXTRA_HANDLERS", [])

        extra_handlers_applied = handlers.apply_extra_handlers(Exception())

        assert extra_handlers_applied == len(handlers.DEFAULT_EXTRA_HANDLERS)

    def test_extra_handlers_calls_string_import(
        self, monkeypatch, mocker, mock_importlib_import_module
    ):
        """Test that extra handlers with string imports are called correctly."""
        # Set default handlers to empty for this test to isolate the settings one.
        monkeypatch.setattr(handlers, "DEFAULT_EXTRA_HANDLERS", [])
        # Make importlib.import_module return the test mock handler when called
        mock_handler = mocker.MagicMock()
        dummy_module = types.SimpleNamespace(mock_handler=mock_handler)
        mock_importlib_import_module.return_value = dummy_module
        # Patch the settings to include the test mock handler
        mocker.patch(
            "drf_simple_api_errors.settings.api_settings.EXTRA_HANDLERS",
            # Add dummy path to have at least one mock handler to import from a string
            ["path.to.module.mock_handler"],
        )

        # exc = mocker.MagicMock()
        exc = Exception()
        extra_handlers_applied = handlers.apply_extra_handlers(exc)

        assert extra_handlers_applied == 1
        mock_handler.assert_called_once_with(exc)

    def test_extra_handlers_calls_multiple(self, mocker, mock_importlib_import_module):
        """
        Test that both default and settings extra handlers are called correctly.
        """
        # Make importlib.import_module return the test mock handler when called
        mock_handler = mocker.MagicMock()
        dummy_module = types.SimpleNamespace(mock_handler=mock_handler)
        mock_importlib_import_module.return_value = dummy_module
        # Patch the settings to include the test mock handler
        mocker.patch(
            "drf_simple_api_errors.settings.api_settings.EXTRA_HANDLERS",
            # Add dummy path to have at least one mock handler to import from a string
            ["path.to.module.mock_handler"],
        )

        # exc = mocker.MagicMock()
        exc = Exception()
        extra_handlers_applied = handlers.apply_extra_handlers(exc)

        assert (
            extra_handlers_applied == len(handlers.DEFAULT_EXTRA_HANDLERS) + 1
        )  # 1 for the settings handler
        mock_handler.assert_called_once_with(exc)

    def test_extra_handlers_value_error_on_non_string_import(self, mocker):
        """
        Test that a ValueError is raised when EXTRA_HANDLERS contains
        a non-string import.
        """
        mocker.patch(
            "drf_simple_api_errors.settings.api_settings.EXTRA_HANDLERS",
            [mocker.MagicMock()],
        )

        with pytest.raises(ValueError) as e:
            handlers.apply_extra_handlers(Exception())

        assert "EXTRA_HANDLERS must be a list of strings" in str(e.value)

    def test_extra_handlers_value_error_when_path_to_extra_handler_not_found(
        self, mocker
    ):
        """
        Test that a ValueError is raised when the path to the extra handler
        does not exist.
        """
        mocker.patch(
            "drf_simple_api_errors.settings.api_settings.EXTRA_HANDLERS",
            ["path.to.non_existent_handler"],
        )

        with pytest.raises(ValueError) as e:
            handlers.apply_extra_handlers(Exception())

        assert "Path path.to.non_existent_handler not found." in str(e.value)

    def test_extra_handlers_value_error_when_extra_handler_is_none(
        self, mocker, mock_importlib_import_module
    ):
        """
        Test that a ValueError is raised when the extra handler is None.
        """
        # Make importlib.import_module return a module without the expected attribute
        dummy_module = types.SimpleNamespace()
        mock_importlib_import_module.return_value = dummy_module
        mocker.patch(
            "drf_simple_api_errors.settings.api_settings.EXTRA_HANDLERS",
            ["path.to.module.non_existent_handler"],
        )

        with pytest.raises(ValueError) as e:
            handlers.apply_extra_handlers(Exception())

        assert "Handler non_existent_handler not found." in str(e.value)

    def test_extra_handlers_value_error_when_extra_handler_not_callable(
        self, mocker, mock_importlib_import_module
    ):
        """
        Test that a ValueError is raised when the extra handler is not callable.
        """
        # Make importlib.import_module return a non-callable attribute
        dummy_module = types.SimpleNamespace(mock_handler="not_a_function")
        mock_importlib_import_module.return_value = dummy_module
        mocker.patch(
            "drf_simple_api_errors.settings.api_settings.EXTRA_HANDLERS",
            ["path.to.module.mock_handler"],
        )

        with pytest.raises(ValueError) as e:
            handlers.apply_extra_handlers(Exception())

        assert "Handler mock_handler is not callable." in str(e.value)


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
