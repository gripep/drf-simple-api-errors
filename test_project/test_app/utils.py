from enum import Enum, unique

from rest_framework.response import Response


@unique
class ErrorTriggers(Enum):
    MODEL_CONSTRAINT = 361
    MODEL_VALIDATION = "Model validation error!"
    SERIALIZER_METHOD = "Serializer method error!"
    SERIALIZER_VALIDATION = "Serializer validation error!"

    def __str__(self) -> str:
        return self.value


def render_response(data: dict) -> dict:
    response = Response(data=data)
    return response.data
