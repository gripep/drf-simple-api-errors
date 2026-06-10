import drf_simple_api_errors.integrations.spectacular as spectacular_module
from drf_simple_api_errors.integrations.spectacular import (
    build_error_component_schemas,
    build_error_response_object,
    postprocess_schema_inject_errors,
)
from drf_simple_api_errors.settings import DEFAULTS

DEFAULT_STATUS_CODES = DEFAULTS["SPECTACULAR_ERROR_STATUS_CODES"]


class TestBuildErrorComponentSchemas:
    """Tests for the ``APIError``/``InvalidParam`` schema builder."""

    def test_snake_case_properties(self, mocker):
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        schemas = build_error_component_schemas()

        assert "APIError" in schemas
        assert "InvalidParam" in schemas

        api_error = schemas["APIError"]
        assert "invalid_params" in api_error["properties"]
        assert "title" in api_error["properties"]
        assert "detail" in api_error["properties"]

    def test_camel_case_properties(self, mocker):
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=True)
        schemas = build_error_component_schemas()

        api_error = schemas["APIError"]
        assert "invalidParams" in api_error["properties"]
        assert "invalid_params" not in api_error["properties"]

    def test_api_error_required_fields(self, mocker):
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        schemas = build_error_component_schemas()
        assert schemas["APIError"]["required"] == ["title"]

    def test_invalid_param_required_fields(self, mocker):
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        schemas = build_error_component_schemas()
        assert set(schemas["InvalidParam"]["required"]) == {"name", "reason"}

    def test_detail_is_nullable(self, mocker):
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        schemas = build_error_component_schemas()
        detail = schemas["APIError"]["properties"]["detail"]
        assert detail["nullable"] is True
        assert detail["type"] == "array"
        assert detail["items"] == {"type": "string"}

    def test_invalid_params_is_nullable(self, mocker):
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        schemas = build_error_component_schemas()
        invalid_params = schemas["APIError"]["properties"]["invalid_params"]
        assert invalid_params["nullable"] is True
        assert invalid_params["items"] == {"$ref": "#/components/schemas/InvalidParam"}

    def test_invalid_param_structure(self, mocker):
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        schemas = build_error_component_schemas()
        ip = schemas["InvalidParam"]
        assert ip["properties"]["name"]["type"] == "string"
        assert ip["properties"]["reason"]["type"] == "array"
        assert ip["properties"]["reason"]["items"] == {"type": "string"}


class TestBuildErrorResponseObject:
    """Tests for the reusable error response object helper."""

    def test_structure(self):
        response = build_error_response_object()
        assert "content" in response
        assert "application/json" in response["content"]
        schema = response["content"]["application/json"]["schema"]
        assert schema == {"$ref": "#/components/schemas/APIError"}


class TestPostprocessSchemaInjectErrors:
    """Tests for the drf-spectacular postprocessing hook."""

    def _minimal_schema(self, operations=None):
        """Build a minimal OpenAPI-like schema dict for testing."""
        schema = {"paths": {}, "components": {"schemas": {}}}
        if operations:
            schema["paths"] = operations
        return schema

    def test_injects_components(self, mocker):
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        schema = self._minimal_schema()
        result = postprocess_schema_inject_errors(result=schema, generator=None)

        assert "APIError" in result["components"]["schemas"]
        assert "InvalidParam" in result["components"]["schemas"]

    def test_does_not_overwrite_existing_components(self, mocker):
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        custom_schema = {"type": "object", "properties": {"custom": {}}}
        schema = self._minimal_schema()
        schema["components"]["schemas"]["APIError"] = custom_schema

        result = postprocess_schema_inject_errors(result=schema, generator=None)
        assert result["components"]["schemas"]["APIError"] is custom_schema

    def test_injects_error_responses_into_operations(self, mocker):
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        schema = self._minimal_schema(
            {
                "/api/items/": {
                    "get": {
                        "responses": {
                            "200": {"description": "OK"},
                        },
                    },
                },
            }
        )
        result = postprocess_schema_inject_errors(result=schema, generator=None)
        responses = result["paths"]["/api/items/"]["get"]["responses"]

        for status_code, description in DEFAULT_STATUS_CODES.items():
            assert status_code in responses
            assert responses[status_code]["description"] == description
            content = responses[status_code]["content"]["application/json"]
            assert content["schema"]["$ref"] == "#/components/schemas/APIError"

    def test_does_not_overwrite_existing_error_responses(self, mocker):
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        custom_400 = {"description": "Custom validation error"}
        schema = self._minimal_schema(
            {
                "/api/items/": {
                    "post": {
                        "responses": {
                            "200": {"description": "OK"},
                            "400": custom_400,
                        },
                    },
                },
            }
        )
        result = postprocess_schema_inject_errors(result=schema, generator=None)
        responses = result["paths"]["/api/items/"]["post"]["responses"]

        # 400 should remain untouched
        assert responses["400"] is custom_400
        # Other error codes should be injected
        assert "401" in responses
        assert "403" in responses

    def test_handles_empty_paths(self, mocker):
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        schema = self._minimal_schema()
        result = postprocess_schema_inject_errors(result=schema, generator=None)
        assert result["paths"] == {}

    def test_skips_non_dict_operations(self, mocker):
        """Path-level parameters or other non-operation entries are skipped."""
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        schema = self._minimal_schema(
            {
                "/api/items/": {
                    "parameters": [{"name": "id", "in": "path"}],
                    "get": {
                        "responses": {"200": {"description": "OK"}},
                    },
                },
            }
        )
        result = postprocess_schema_inject_errors(result=schema, generator=None)
        # parameters should be unchanged, get should have error responses
        assert isinstance(result["paths"]["/api/items/"]["parameters"], list)
        assert "400" in result["paths"]["/api/items/"]["get"]["responses"]

    def test_custom_status_codes(self, mocker):
        """Only configured status codes are injected."""
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        mocker.patch(
            "drf_simple_api_errors.integrations.spectacular.api_settings"
            ".SPECTACULAR_ERROR_STATUS_CODES",
            new={"400": "Validation error"},
        )
        schema = self._minimal_schema(
            {
                "/api/items/": {
                    "get": {
                        "responses": {"200": {"description": "OK"}},
                    },
                },
            }
        )
        result = postprocess_schema_inject_errors(result=schema, generator=None)
        responses = result["paths"]["/api/items/"]["get"]["responses"]

        assert "400" in responses
        assert "401" not in responses
        assert "403" not in responses
        assert "404" not in responses
        assert "500" not in responses

    def test_empty_status_codes_injects_components_only(self, mocker):
        """Empty status codes setting injects schemas but no responses."""
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        mocker.patch(
            "drf_simple_api_errors.integrations.spectacular.api_settings"
            ".SPECTACULAR_ERROR_STATUS_CODES",
            new={},
        )
        schema = self._minimal_schema(
            {
                "/api/items/": {
                    "get": {
                        "responses": {"200": {"description": "OK"}},
                    },
                },
            }
        )
        result = postprocess_schema_inject_errors(result=schema, generator=None)

        # Components should still be injected
        assert "APIError" in result["components"]["schemas"]
        assert "InvalidParam" in result["components"]["schemas"]
        # No error responses should be added
        responses = result["paths"]["/api/items/"]["get"]["responses"]
        assert list(responses.keys()) == ["200"]


class TestNoDrfSpectacularDependency:
    """
    Tests that the integration module is importable and fully functional
    without drf-spectacular installed, so that projects that don't use the
    extra are unaffected.
    """

    def test_module_does_not_import_drf_spectacular(self):
        # No top-level binding to drf_spectacular in the integration module.
        for name, value in vars(spectacular_module).items():
            module_name = getattr(value, "__module__", "") or ""
            assert not module_name.startswith(
                "drf_spectacular"
            ), f"{name!r} is sourced from drf_spectacular"

    def test_public_api_runs_without_drf_spectacular(self, mocker):
        mocker.patch("drf_simple_api_errors.utils.api_settings.CAMELIZE", new=False)
        # Exercise every public callable; none of them should require
        # drf-spectacular to be importable.
        schemas = build_error_component_schemas()
        assert "APIError" in schemas and "InvalidParam" in schemas

        response = build_error_response_object()
        assert response["content"]["application/json"]["schema"] == {
            "$ref": "#/components/schemas/APIError"
        }

        result = postprocess_schema_inject_errors(
            result={"paths": {}, "components": {"schemas": {}}},
            generator=None,
        )
        assert "APIError" in result["components"]["schemas"]
