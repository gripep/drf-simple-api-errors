from rest_framework.response import Response


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
