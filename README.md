# Django Rest Framework Simple API Errors

## What is this?

A library for [Django Rest Framework](https://www.django-rest-framework.org/) returning **consistent and easy-to-parse API error messages**.

This library was built with [RFC7807](https://tools.ietf.org/html/rfc7807) guidelines in mind, but with a small twist: it defines a "problem detail" as a `list` but it still serves as a way to include errors in a predictable and easy-to-parse format for any API consumer.

Errors are formatted with RFC7807 keywords and DRF exception data.
This library was designed to be used by anyone who had enough of DRF API error messages format.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Exception Handler](#exception-handler)
  - [Error structure overview](#error-structure-overview)
  - [Example JSON Error Responses](#example-json-error-responses)
  - [Settings](#settings)
    - [CAMELIZE](#camelize)
    - [EXTRA_HANDLERS](#extra_handlers)
    - [FIELDS_SEPARATOR](#fields_separator)
- [Testing](#testing)
- [Support](#support)
- [Contributing](#contributing)

## Installation

Install using the command line:

```
pip install drf-simple-api-errors
```

## Usage

### Exception Handler

Add `EXCEPTION_HANDLER` in your `REST_FRAMEWORK` settings of your Django project settings file:

```python
REST_FRAMEWORK = {
    # ...
    "EXCEPTION_HANDLER": "drf_simple_api_errors.exception_handler",
}
```

### Error structure overview

API error messages typically include the following keys:

- `"title"` (`str`): A brief summary that describes the problem type
- `"detail"` (`list[str] | None`): A list of specific explanations related to the problem
- `"invalid_params"` (`list[dict] | None`): A list of strings containing details about parameters that were invalid or malformed in the request. Each object within this list provides:
  - `"name"` (`str`): The name of the parameter that was found to be invalid.
  - `"reasons"` (`list[str]`): A list of strings describing the specific issues or reasons why the parameter was considered invalid or malformed.

```json
{
    "title": "Error message.",
    "detail": [
        "error",
        ...
    ],
    "invalid_params": [
        {
            "name": "field_name",
            "reason": [
                "error",
                ...
            ]
        },
        ...
    ]
}
```

### Example JSON Error Responses

#### Field validation errors

```json
{
    "title": "Error message.",
    "invalid_params": [
        {
            "name": "field_name",
            "reason": [
                "error",
                ...
            ]
        },
        ...
    ]
}
```

#### Non-fields validation errors

```json
{
  "title": "Error message.",
  "detail": [
    "error",
    ...
  ]
}
```

#### Other bad requests with no detail

```json
{
  "title": "Error message."
}
```

## Settings

Default available settings:

```python
DRF_SIMPLE_API_ERRORS = {
    "CAMELIZE": False,
    "EXTRA_HANDLERS": [],
    "FIELDS_SEPARATOR": ".",
}
```

- #### CAMELIZE

Camel case support for Django Rest Framework exceptions JSON error responses.

If `CAMELIZE` is set to `True`:

```json
{
  "title": "Error message.",
  "invalidParams": [
    {
      "name": "fieldName",
      "reason": [
        "error",
        ...
      ]
    }
    ...
  ]
}
```

- #### EXTRA_HANDLERS

Support for exceptions that differ from the standard structure of the Django Rest Framework.

For instance, you may want to specify you own exception:

```python
class AuthenticationFailed(exceptions.AuthenticationFailed):
    def __init__(self, detail=None, code=None):
        """
        Builds a detail dictionary for the error to give more information
        to API users.
        """
        detail_dict = {"detail": self.default_detail, "code": self.default_code}

        if isinstance(detail, dict):
            detail_dict.update(detail)
        elif detail is not None:
            detail_dict["detail"] = detail

        if code is not None:
            detail_dict["code"] = code

        super().__init__(detail_dict)
```

Use exception in code:

```python
def my_func():
    raise AuthenticationFailed(
        {
            "detail": _("Error message."),
            "messages": [
                {
                    "metadata": "metadata_data",
                    "type": "type_name",
                    "message": "error message",
                }
            ],
        }
    )
```

This will result in:

```python
AuthenticationFailed(
    {
        "detail": "Error message.",
        "messages": [
            {
                "metadata": "metadata_data",
                "type": "type_name",
                "message": "error message",
            }
        ],
    }
)
```

You can handle this by creating a `handlers.py` file and specifying an handler for your use case:

```python
def handle_exc_custom_authentication_failed(exc):
    from path.to.my.exceptions import AuthenticationFailed

    if isinstance(exc, AuthenticationFailed):
        try:
            exc.detail = exc.detail["messages"][0]["message"]
        except (KeyError, IndexError):
            exc.detail = exc.detail["detail"]

    return exc
```

Then add it to the `EXTRA_HANDLERS` list in this package settings:

```python
DRF_SIMPLE_API_ERRORS = {
    "EXTRA_HANDLERS": [
        "path.to.my.handlers.handle_exc_custom_authentication_failed",
        # ...
    ]
}
```

- #### FIELDS_SEPARATOR

Support for nested dicts containing multiple fields to be flattened.

If `FIELDS_SEPARATOR` is set to `.`:

```python
{
    "field1": {
        "field2": "value"
    }
}
```

Will result in:

```python
{
    "field1.field2": "value"
}
```

## Testing

All the necessary commands are included in the `Makefile`.

We are using `tox` and `poetry` to run tests in every supported Python version.

Run test with the commands below:

```
make install
make test
```

## Support

Please [open an issue](https://github.com/gripep/drf-simple-api-errors/issues/new).

## Contributing

Please use the [Github Flow](https://guides.github.com/introduction/flow/). In a nutshell, create a branch, commit your code, and open a pull request.
