from enum import Enum, unique

from rest_framework.response import Response


@unique
class ErrorTriggers(Enum):
    """Enum for error triggers used in tests and examples."""

    MODEL_CONSTRAINT = 361
    MODEL_VALIDATION = "Model validation error!"
    SERIALIZER_METHOD = "Serializer method error!"
    SERIALIZER_VALIDATION = "Serializer validation error!"

    def __str__(self) -> str:
        return self.value


def render_response(data: dict) -> dict:
    """
    Renders the response data from a `dict` to a DRF Response object.

    Args:
        data (dict): The data to be rendered.

    Returns:
        response.data (dict): The rendered response data from the DRF `Response` object.
    """
    # This is needed in tests to ensure that
    # the response data is in the same format as the DRF Response given by
    # the exception handler.
    response = Response(data=data)
    return response.data
