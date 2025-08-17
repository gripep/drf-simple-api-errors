"""
This module provides functionality to format API exceptions into a structured
error response.

It defines the `APIErrorResponse` class, which represents
the structure of the error response, and the `format_exc` function, which
formats exceptions into this structure according to the type of exception, its detail,
and any additional settings defined in the settings.

Functions:
    - `format_exc`:
        Formats the given exception into a structured API error response.
        Used by the exception handler to return a consistent error format.
"""

import copy
import logging
from dataclasses import asdict, dataclass, field as dataclass_field
from typing import Dict, List, Optional

from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.settings import api_settings as drf_api_settings

from drf_simple_api_errors import utils
from drf_simple_api_errors.types import APIErrorResponseDict

logger = logging.getLogger(__name__)


@dataclass
class InvalidParam:
    """
    A class representing an invalid parameter in the API error response.

    This is used within the `APIErrorResponse` class to represent
    parameters that are invalid and have errors associated with them.
    """

    name: str
    reason: List[str]


@dataclass
class APIErrorResponse:
    """
    A class representing the API error response structure.

    It includes:
        - title: A short, human-readable summary of the error
        - detail: A more detailed explanation of the error, if any
        - invalid_params: A list of invalid parameters, if any
    """

    title: str = dataclass_field(default="")
    detail: Optional[List[str]] = dataclass_field(default=None)
    invalid_params: Optional[List[InvalidParam]] = dataclass_field(default=None)

    def to_dict(self) -> APIErrorResponseDict:
        """Convert the APIErrorResponse instance to a dictionary."""
        response_dict = asdict(self)

        for key in list(response_dict.keys()):
            response_dict[utils.camelize(key)] = response_dict.pop(key)

        return response_dict


def format_exc(exc: exceptions.APIException) -> APIErrorResponseDict:
    """
    Format the exception into a structured API error response.

    Args:
        exc (APIException): The exception to format.
    Returns:
        APIErrorResponseDict:
            A structured dictionary representing the API error response.
    """
    data = APIErrorResponse()

    # Set the API error response...
    if isinstance(exc, exceptions.ValidationError):
        # If the exception is a ValidationError,
        # set the title to "Validation Error."
        data.title = _("Validation error.")
    else:
        # If the exception is not a ValidationError,
        # set the title to its default detail, e.g. "Not Found."
        data.title = exc.default_detail
        if _is_exc_detail_same_as_default_detail(exc):
            # If the exception detail is the same as the default detail,
            # we don't need to format it and return it as is, because
            # it is not providing any additional information about the error.
            return data.to_dict()

    # Extract the exception detail based on the type of exception.
    # There are cases where the exc detail is a str, e.g. APIException("Error"),
    # we will convert it to a list so that we can handle it uniformly.
    exc_detail = exc.detail if not isinstance(exc.detail, str) else [exc.detail]
    logger.debug("'exc_detail' is instance of %s" % type(exc_detail))
    # Create the API error response based on the exception detail...
    if isinstance(exc_detail, dict):
        return _format_exc_detail_dict(data, exc_detail)
    else:
        # If the exception detail in not a dict, it must be a list, and
        # we will return all the errors in a single list.
        return _format_exc_detail_list(data, exc_detail)


def _format_exc_detail_dict(
    data: APIErrorResponse, exc_detail: Dict
) -> APIErrorResponseDict:
    """
    Handle the exception detail as a dictionary.

    Args:
        data (APIErrorResponse): The data dictionary to update.
        exc_detail (dict): The exception detail dictionary.

    Returns:
        APIErrorResponseDict: The updated `data` dictionary.
    """
    # Start by flattening the exc dict.
    # This is necessary as the exception detail can be nested and
    # we want to flatten it to a single level dict as part of this library design.
    exc_detail = utils.flatten_dict(copy.deepcopy(exc_detail))

    # Track the invalid params.
    # This represents the fields that are invalid and have errors associated with them.
    invalid_params = []
    # Track the non-field errors.
    # This represents the errors that are not associated with any specific field.
    # For example, this happens when an error is raised on the serializer level
    # and not on the field level, e.g. in Serializer.validate() method.
    non_field_errors = []
    # Now gather the errors by iterating over the exception detail.
    for field, error in exc_detail.items():
        if field in [drf_api_settings.NON_FIELD_ERRORS_KEY, "__all__"]:
            # We are first going to check if field represents a non-field error.
            # These errors are usually general and not associated with any field.
            if isinstance(error, list):
                non_field_errors.extend(error)
            else:
                non_field_errors.append(error)
        else:
            # Otherwise, we will treat it as an invalid param.
            # N.B. If the error is a string, we will convert it to a list
            # to keep the consistency with the InvalidParamDict type.
            invalid_param = InvalidParam(
                name=utils.camelize(field),
                reason=error if isinstance(error, list) else [error],
            )
            invalid_params.append(invalid_param)

    if invalid_params:
        data.invalid_params = invalid_params

    if non_field_errors:
        data.detail = non_field_errors

    return data.to_dict()


def _format_exc_detail_list(
    data: APIErrorResponse, exc_detail: List
) -> APIErrorResponseDict:
    """
    Handle the exception detail as a list.

    Args:
        data (APIErrorResponse): The data dictionary to update.
        exc_detail (list): The exception detail list.

    Returns:
        APIErrorResponseDict: The updated `data` dictionary.
    """
    detail = []

    for error in exc_detail:
        if isinstance(error, str):
            detail.append(error)
        elif isinstance(error, list):
            detail.extend(error)
        else:
            # This is necessary as there is definitely something unexpected
            # in the exc detail!
            # This could be a potential bug in the code or a new feature in DRF/Django.
            # Please report this to the maintainer if this ever happens
            raise TypeError(
                "Unexpected type for error in exception detail. "
                "Expected str or list, got %s.",
                type(error),
            )

    if detail:
        data.detail = detail

    return data.to_dict()


def _is_exc_detail_same_as_default_detail(exc: exceptions.APIException) -> bool:
    """
    Check if the exception detail is the same as the default detail.

    The default detail is the message that is the generic message
    for the exception type.
    For example, the default detail for `NotFound` is "Not found.", so
    if the detail is the same as the default detail, we can assume that
    the exception is not providing any additional information about the error and
    we can ignore it.

    Args:
        exc (APIException): The exception to check.

    Returns:
        bool:
            True if the exception detail is the same as the default detail,
            False otherwise.
    """
    return (isinstance(exc.detail, str) and exc.detail == exc.default_detail) or (
        isinstance(exc.detail, list)
        and len(exc.detail) == 1
        and isinstance(exc.detail[0], str)
        and exc.detail[0] == exc.default_detail
    )
