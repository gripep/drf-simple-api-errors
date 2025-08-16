# Django Rest Framework Simple API Errors

![PyPI](https://img.shields.io/pypi/v/drf-simple-api-errors)
![test workflow](https://github.com/gripep/drf-simple-api-errors/actions/workflows/build.yaml/badge.svg)
[![codecov](https://codecov.io/gh/gripep/drf-simple-api-errors/graph/badge.svg?token=1LJV518KMD)](https://codecov.io/gh/gripep/drf-simple-api-errors)
![pyversions](https://img.shields.io/pypi/pyversions/drf-simple-api-errors.svg)

## What is this?

A library for [Django Rest Framework](https://www.django-rest-framework.org/) returning **consistent, predictable and easy-to-parse API error messages**.

This library was built with [RFC7807](https://tools.ietf.org/html/rfc7807) guidelines in mind, but with a small twist: it defines a "problem detail" as a list instead of a string, but it still serves as a way to include errors in a human-readable and easy-to-parse format for any API consumer.
Error messages are formatted using RFC7807 keywords and DRF exception data.

Unlike standard DRF, where the error response format varies depending on the error source, this library always returns errors in a consistent and predictable structure.

## What's different?

Compared to other similar and popular libraries, this library:

- Is based on RFC7807 guidelines
- Aims to provide not only a standardized format for error details, but also human-readable error messages (perfect for both internal and public APIs)
- Transforms both `django.core.exceptions.ValidationError` and `rest_framework.errors.ValidationError` to API errors, so you don't have to handle error raised by services/domain logic, `clean()`, etc.

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

API error messages will include the following keys:

- `"title"` (`str`): A brief summary that describes the problem type.
- `"detail"` (`list[str] | None`): A list of specific explanations related to the problem, if any.
- `"invalid_params"` (`list[dict] | None`): A list of dict containing details about parameters that were invalid or malformed in the request, if any. Each dict within this list provides:
  - `"name"` (`str`): The name of the parameter that was found to be invalid.
  - `"reasons"` (`list[str]`): A list of strings describing the specific reasons why the parameter was considered invalid or malformed.

```json
{
  "title": "Error message.",
  "detail": ["error"],
  "invalid_params": [
    {
      "name": "field_name",
      "reason": ["error"]
    }
  ]
}
```

### Example JSON Error Responses

#### Field validation errors

```json
{
  "title": "Error message.",
  "details": null,
  "invalid_params": [
    {
      "name": "field_name",
      "reason": ["error"]
    }
  ]
}
```

#### Non-fields validation errors

```json
{
  "title": "Error message.",
  "detail": ["error"],
  "invalid_params": null
}
```

#### Other bad requests with no detail

```json
{
  "title": "Error message.",
  "detail": null,
  "invalid_params": null
}
```

## Settings

Default settings:

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
  "details": null,
  "invalidParams": [
    {
      "name": "fieldName",
      "reason": ["error"]
    }
  ]
}
```

- #### EXTRA_HANDLERS

Support for exceptions that differ from the standard structure of the Django Rest Framework.

For example, if you need to customize how a specific exception is handled or want to format an existing exception differently, you can create your own handler.

To customize error handling for your project, simply create a new file (for example, `extra_handlers.py`) and define your own handler functions. This approach lets you tailor error responses to fit your specific needs.

Then add it to the `EXTRA_HANDLERS` list in this package settings:

```python
DRF_SIMPLE_API_ERRORS = {
    "EXTRA_HANDLERS": [
        "path.to.my.extra_handlers.custom_handler",
        # ...
    ]
}
```

For reference, this library uses the same pattern for its own extra handlers [here](drf_simple_api_errors/extra_handlers.py).

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

Run test during development with the commands below:

```
make install  # only if necessary
make test
```

Finally, run `tox` to ensure the changes work for every supported python version:

```
pip install tox  # only if necessary
tox -v
```

## Support

Please [open an issue](https://github.com/gripep/drf-simple-api-errors/issues/new).

## Contributing

Please use the [Github Flow](https://guides.github.com/introduction/flow/). In a nutshell, create a branch, commit your code, and open a pull request.
