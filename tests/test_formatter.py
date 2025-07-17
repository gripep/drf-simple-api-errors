from rest_framework import exceptions as drf_exceptions

import pytest

from drf_simple_api_errors import formatter


class TestAPIErrorResponse:
    def test_init(self):
        """
        Test the initialization of APIErrorResponse.

        This checks that the default values are set correctly.
        In our use case, all the fields are eventually set when the
        exception is evaluated.
        """
        response = formatter.APIErrorResponse()

        assert response.title == ""
        assert response.detail is None
        assert response.invalid_params is None

    def test_to_dict(self):
        """Test the conversion of APIErrorResponse to dictionary."""
        response = formatter.APIErrorResponse(
            title="Error Title",
            detail=["Detail 1", "Detail 2"],
            invalid_params=[
                formatter.InvalidParam(name="param1", reason=["Invalid type"]),
                formatter.InvalidParam(
                    name="param2", reason=["Required field missing"]
                ),
            ],
        )

        expected_dict = {
            "title": "Error Title",
            "detail": ["Detail 1", "Detail 2"],
            "invalid_params": [
                {"name": "param1", "reason": ["Invalid type"]},
                {"name": "param2", "reason": ["Required field missing"]},
            ],
        }
        assert response.to_dict() == expected_dict

    def test_to_dict_if_camelize_is_true(self, mocker):
        """
        Test the conversion of APIErrorResponse to dictionary when
        camelize setting is True.
        """
        mocker.patch("drf_simple_api_errors.settings.api_settings.CAMELIZE", True)

        response = formatter.APIErrorResponse(
            title="Error Title",
            detail=["Detail 1", "Detail 2"],
            invalid_params=[
                formatter.InvalidParam(name="param1", reason=["Invalid type"]),
                formatter.InvalidParam(
                    name="param2", reason=["Required field missing"]
                ),
            ],
        )

        expected_dict = {
            "title": "Error Title",
            "detail": ["Detail 1", "Detail 2"],
            "invalidParams": [
                {"name": "param1", "reason": ["Invalid type"]},
                {"name": "param2", "reason": ["Required field missing"]},
            ],
        }
        assert response.to_dict() == expected_dict


class TestFormatExc:
    def test_title_set_when_validation_error(self):
        """
        Test that the title is set to "Validation Error" for ValidationError exceptions.
        """
        exc = drf_exceptions.ValidationError()

        data = formatter.format_exc(exc)
        assert data["title"] == "Validation error."

    @pytest.mark.parametrize(
        "exc, expected_title",
        [
            (drf_exceptions.NotFound(), "Not found."),
            # Exc detail is populated but title is unchanged
            (
                drf_exceptions.AuthenticationFailed("Bad credentials."),
                "Incorrect authentication credentials.",
            ),
        ],
    )
    def test_title_set_with_exception_title(self, exc, expected_title):
        """
        Test that the title is set correctly for various exceptions.
        """
        data = formatter.format_exc(exc)
        assert data["title"] == expected_title

    def test_title_set_when_exception_detail_is_the_same_as_default_detail(self):
        """
        Test that when the exception detail is the same as the default detail,
        only the title is set and the detail is `None`.
        """
        exc = drf_exceptions.NotFound("Not found.")

        data = formatter.format_exc(exc)
        assert data["title"] == "Not found."
        assert data["detail"] is None

    @pytest.mark.parametrize(
        "exc, expected_invalid_params",
        [
            (
                drf_exceptions.ValidationError({"field": ["This field is required."]}),
                [{"name": "field", "reason": ["This field is required."]}],
            ),
            # The field error detail is not a list, so it should be converted to a list.
            (
                drf_exceptions.ValidationError({"field": "This field is required."}),
                [{"name": "field", "reason": ["This field is required."]}],
            ),
            # Multiple fields with errors
            (
                drf_exceptions.ValidationError(
                    {"field1": ["This field is required."], "field2": "Invalid value."}
                ),
                [
                    {"name": "field1", "reason": ["This field is required."]},
                    {"name": "field2", "reason": ["Invalid value."]},
                ],
            ),
            # Nested fields with errors
            (
                drf_exceptions.ValidationError(
                    {
                        "field1": {"subfield": ["This subfield is required."]},
                        "field2": "Invalid value.",
                    }
                ),
                [
                    {
                        "name": "field1.subfield",
                        "reason": ["This subfield is required."],
                    },
                    {"name": "field2", "reason": ["Invalid value."]},
                ],
            ),
        ],
    )
    def test_exc_detail_is_dict_with_invalid_params(self, exc, expected_invalid_params):
        """
        Test that the exception detail is correctly formatted
        when it contains invalid parameters.
        The detail should be `None` and invalid_params should be populated.
        """
        data = formatter.format_exc(exc)
        assert data["detail"] is None
        assert data["invalid_params"] == expected_invalid_params

    @pytest.mark.parametrize(
        "non_field_errors_key", ["non_field_errors", "nonFieldErrors", "__all__"]
    )
    def test_exc_detail_is_dict_with_non_field_errors(
        self, mocker, non_field_errors_key
    ):
        """
        Test that when the exception detail is a dict with non-field errors,
        the detail is set to the error messages and invalid_params is None.
        """
        if non_field_errors_key != "__all__":
            # Mock the non_field_errors_key setting if it's not "__all__"
            # The key "__all__" is normally by ModelSerializer and
            # is not part of the DRF settings.
            mocker.patch(
                "rest_framework.settings.api_settings.NON_FIELD_ERRORS_KEY",
                non_field_errors_key,
            )

        exc = drf_exceptions.ValidationError(
            {non_field_errors_key: ["This is a non-field error."]}
        )

        data = formatter.format_exc(exc)
        assert data["detail"] == ["This is a non-field error."]
        assert data["invalid_params"] is None

    @pytest.mark.parametrize(
        "exc_detail",
        [
            ["This is a non-field error."],
            "This is a non-field error.",
        ],
    )
    def test_exc_detail_is_dict_with_non_field_errors_formats(self, mocker, exc_detail):
        """
        Test that when the non field errors are provided in different formats,
        the detail is set to the error messages list and invalid_params is `None`.
        """
        exc = drf_exceptions.ValidationError({"non_field_errors": exc_detail})

        data = formatter.format_exc(exc)
        assert data["detail"] == ["This is a non-field error."]
        assert data["invalid_params"] is None

    @pytest.mark.parametrize(
        "exc_detail, expected_detail",
        [
            ("This is a non-field error.", ["This is a non-field error."]),
            (["This is a non-field error."], ["This is a non-field error."]),
            (
                ["This is a non-field error.", "Another error."],
                ["This is a non-field error.", "Another error."],
            ),
            (
                [
                    "This is a non-field error.",
                    ["Another error.", "Yet another error."],
                ],
                ["This is a non-field error.", "Another error.", "Yet another error."],
            ),
        ],
    )
    def test_exc_detail_is_list_formats(self, exc_detail, expected_detail):
        """
        Test that when the exception detail is a list or a string,
        the detail is set to the error messages list and invalid_params is `None`.
        """
        exc = drf_exceptions.ValidationError(exc_detail)

        data = formatter.format_exc(exc)
        assert data["detail"] == expected_detail
        assert data["invalid_params"] is None

    def test_format_exc_detail_is_list_error_when_unexpected_type(self):
        """
        Test that when the exception detail is an unexpected type,
        it raises a TypeError.
        """
        with pytest.raises(TypeError):
            formatter.format_exc(
                drf_exceptions.ValidationError([{"question": "What are you doing?"}])
            )
