"""
Types for exception handler and its modules.
"""

from typing import Dict, List, Optional, Tuple, TypedDict

from rest_framework.request import Request
from rest_framework.views import APIView


class ExceptionHandlerContext(TypedDict):
    """
    The base interface for the context of the exception handler.

    This is passed to the exception handler function and contains
    information about the request and view.
    """

    view: APIView
    args: Tuple
    kwargs: Dict
    request: Optional[Request]


class InvalidParamDict(TypedDict):
    """The base interface for the invalid parameters in the API error response."""

    name: str
    reason: List[str]


class APIErrorResponseDict(TypedDict):
    """
    The base interface for the API error response.
    This is the response returned by the exception handler.
    """

    title: str
    detail: Optional[List[str]]
    invalid_params: Optional[List[InvalidParamDict]]
