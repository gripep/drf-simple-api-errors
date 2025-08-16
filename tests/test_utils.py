import pytest

from drf_simple_api_errors import utils


class TestCamelize:
    """Test cases for the camelize function in utils module."""

    @pytest.mark.parametrize(
        "field_input, expected_output",
        [
            ("", ""),
            ("name", "name"),
            ("first_name", "firstName"),
            ("family_tree_name", "familyTreeName"),
            ("very_long_last_name_and_first_name", "veryLongLastNameAndFirstName"),
            # This is a special case where the underscore is at the start
            # and should NOT be removed.
            ("_special", "_special"),
        ],
    )
    def test_with_camelize_settings_true(self, mocker, field_input, expected_output):
        """Test conversion to camelCase when CAMELIZE setting is True."""
        mocker.patch("drf_simple_api_errors.settings.api_settings.CAMELIZE", True)

        assert utils.camelize(field_input) == expected_output

    @pytest.mark.parametrize(
        "field_input, expected_output",
        [
            ("", ""),
            ("name", "name"),
            ("first_name", "first_name"),
            ("family_tree_name", "family_tree_name"),
            (
                "very_long_last_name_and_first_name",
                "very_long_last_name_and_first_name",
            ),
            ("_special", "_special"),
        ],
    )
    def test_with_camelize_settings_false(self, field_input, expected_output):
        """Test no conversion to camelCase when CAMELIZE setting is False (default)."""
        assert utils.camelize(field_input) == expected_output


class TestFlattenDict:
    """Test cases for the flatten_dict function in utils module."""

    @pytest.mark.parametrize(
        "original_dict, flattened_dict",
        [
            ({"key": "value"}, {"key": "value"}),
            ({"key": {"subkey": "value"}}, {"key.subkey": "value"}),
            (
                {"key": {"subkey": {"subsubkey": "value"}}},
                {"key.subkey.subsubkey": "value"},
            ),
            (
                {"key": {"subkey": "value", "subkey2": "value2"}},
                {"key.subkey": "value", "key.subkey2": "value2"},
            ),
            (
                {"key": {"subkey": {"subsubkey": "value", "subsubkey2": "value2"}}},
                {"key.subkey.subsubkey": "value", "key.subkey.subsubkey2": "value2"},
            ),
        ],
    )
    def test_with_default_field_separator(self, original_dict, flattened_dict):
        """Test flattening a dictionary with default field separator."""
        assert utils.flatten_dict(original_dict) == flattened_dict

    def test_with_different_field_separator_settings(self, mocker):
        """Test flattening a dictionary with a custom field separator."""
        new_separator = "_"
        mocker.patch(
            "drf_simple_api_errors.settings.api_settings.FIELDS_SEPARATOR",
            new_separator,
        )

        original_dict = {"key": {"subkey": "value"}}

        expected_result = {f"key{new_separator}subkey": "value"}
        assert utils.flatten_dict(original_dict) == expected_result
