from django.core.exceptions import ValidationError
from rest_framework import exceptions

import pytest

from drf_simple_api_errors import exception_handler
from test_app.utils import ErrorTriggers, render_response


@pytest.mark.django_db
class TestSerializerErrors:
    def test_field_required_error_ok(self, book_serializer, mocker):
        serializer = book_serializer(data={})
        with pytest.raises(exceptions.ValidationError):
            exc = serializer.is_valid(raise_exception=True)
            response = exception_handler(exc, mocker.Mock())

            expected_response = {
                "title": "Validation error.",
                "detail": None,
                "invalid_params": [
                    {
                        "name": "title",
                        "reason": ["This field is required."],
                    },
                    {
                        "name": "pages",
                        "reason": ["This field is required."],
                    },
                    {
                        "name": "isbn10",
                        "reason": ["This field is required."],
                    },
                ],
            }
            assert render_response(response.data) == expected_response

    def test_field_validation_error_ok(self, book, book_serializer, faker, mocker):
        data = {
            "isbn10": book.isbn10,
            "pages": faker.pyint(max_value=360),
            "title": faker.word()[:32],  # slice not to exceed max_length
        }

        serializer = book_serializer(data=data)
        with pytest.raises(exceptions.ValidationError):
            exc = serializer.is_valid(raise_exception=True)
            response = exception_handler(exc, mocker.Mock())

            expected_response = {
                "title": "Validation error.",
                "detail": None,
                "invalid_params": [
                    {
                        "name": "isbn10",
                        "reason": [f"Book with isbn10 {book.isbn10} already exists."],
                    }
                ],
            }
            assert render_response(response.data) == expected_response

    def test_validation_error_ok(self, book_serializer, faker, mocker):
        data = {
            "isbn10": faker.unique.isbn10(),
            "pages": faker.pyint(max_value=360),
            "title": ErrorTriggers.SERIALIZER_VALIDATION.value,
        }

        serializer = book_serializer(data=data)
        with pytest.raises(exceptions.ValidationError):
            exc = serializer.is_valid(raise_exception=True)
            response = exception_handler(exc, mocker.Mock())

            expected_response = {
                "title": "Validation error.",
                "detail": [f"Title cannot be {ErrorTriggers.SERIALIZER_VALIDATION}"],
                "invalid_params": None,
            }
            assert render_response(response.data) == expected_response


@pytest.mark.django_db
class TestModelSerializerErrors:
    def test_bad_choice_error_ok(self, book_model_serializer, faker, mocker, user):
        edition = faker.word()[:8]
        data = {
            "author": user.username,
            "edition": edition,
            "isbn10": faker.unique.isbn10(),
            "pages": faker.pyint(max_value=360),
            "title": faker.word()[:32],
        }

        serializer = book_model_serializer(data=data)
        with pytest.raises(exceptions.ValidationError):
            exc = serializer.is_valid(raise_exception=True)
            response = exception_handler(exc, mocker.Mock())

            expected_response = {
                "title": "Validation error.",
                "detail": None,
                "invalid_params": [
                    {
                        "name": "edition",
                        "reason": [f'"{edition}" is not a valid choice.'],
                    }
                ],
            }
            assert render_response(response.data) == expected_response

    def test_bad_one_to_one_relationship_error_ok(
        self, book_model_serializer, faker, mocker
    ):
        username = faker.user_name()
        data = {
            "author": username,
            "isbn10": faker.unique.isbn10(),
            "pages": ErrorTriggers.MODEL_CONSTRAINT.value,
            "title": faker.word()[:32],
        }

        serializer = book_model_serializer(data=data)
        with pytest.raises(exceptions.ValidationError):
            serializer.is_valid(raise_exception=True)
            exc = serializer.save()
            response = exception_handler(exc, mocker.Mock())

            expected_response = {
                "title": "Validation error.",
                "detail": None,
                "invalid_params": [
                    {
                        "name": "author",
                        "reason": [f"Object with username={username} does not exist."],
                    }
                ],
            }
            assert render_response(response.data) == expected_response

    def test_bad_many_to_many_relationship_error_ok(
        self, book_model_serializer, faker, mocker, user
    ):
        library_name1, library_name2 = faker.word()[:32], faker.word()[:32]
        data = {
            "author": user.username,
            "isbn10": faker.unique.isbn10(),
            "libraries": [library_name1, library_name2],
            "pages": faker.pyint(max_value=360),
            "title": faker.word()[:32],
        }

        serializer = book_model_serializer(data=data)
        with pytest.raises(exceptions.ValidationError):
            serializer.is_valid(raise_exception=True)
            exc = serializer.save()
            response = exception_handler(exc, mocker.Mock())

            expected_response = {
                "title": "Validation error.",
                "detail": None,
                "invalid_params": [
                    {
                        "name": "libraries",
                        "reason": [f"Object with name={library_name1} does not exist."],
                    }
                ],
            }
            assert render_response(response.data) == expected_response

    def test_constraint_error_ok(self, book_model_serializer, faker, mocker, user):
        data = {
            "author": user.username,
            "isbn10": faker.unique.isbn10(),
            "pages": ErrorTriggers.MODEL_CONSTRAINT.value,
            "title": faker.word()[:32],
        }

        serializer = book_model_serializer(data=data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
            exc = serializer.save()
            response = exception_handler(exc, mocker.Mock())

            expected_response = {
                "title": "Validation error.",
                "detail": ["Pages cannot be more than 360."],
                "invalid_params": None,
            }
            assert render_response(response.data) == expected_response

    def test_field_required_error_ok(self, book_model_serializer, mocker):
        serializer = book_model_serializer(data={})
        with pytest.raises(exceptions.ValidationError):
            exc = serializer.is_valid(raise_exception=True)
            response = exception_handler(exc, mocker.Mock())

            expected_response = {
                "title": "Validation error.",
                "detail": None,
                "invalid_params": [
                    {
                        "name": "author",
                        "reason": ["This field is required."],
                    },
                    {
                        "name": "isbn10",
                        "reason": ["This field is required."],
                    },
                    {
                        "name": "pages",
                        "reason": ["This field is required."],
                    },
                    {
                        "name": "title",
                        "reason": ["This field is required."],
                    },
                ],
            }
            assert render_response(response.data) == expected_response

    def test_method_error_ok(self, book_model_serializer, faker, mocker, user):
        data = {
            "author": user.username,
            "isbn10": faker.unique.isbn10(),
            "pages": faker.pyint(max_value=360),
            "title": ErrorTriggers.SERIALIZER_METHOD.value,
        }

        serializer = book_model_serializer(data=data)
        with pytest.raises(exceptions.ValidationError):
            serializer.is_valid(raise_exception=True)
            exc = serializer.save()
            response = exception_handler(exc, mocker.Mock())

            expected_response = {
                "title": "Validation error.",
                "detail": [ErrorTriggers.SERIALIZER_METHOD.value],
                "invalid_params": None,
            }
            assert render_response(response.data) == expected_response

    def test_validation_error_ok(self, book_model_serializer, faker, mocker, user):
        data = {
            "author": user.username,
            "isbn10": faker.unique.isbn10(),
            "pages": faker.pyint(max_value=360),
            "title": ErrorTriggers.SERIALIZER_VALIDATION.value,
        }

        serializer = book_model_serializer(data=data)
        with pytest.raises(exceptions.ValidationError):
            exc = serializer.is_valid(raise_exception=True)
            response = exception_handler(exc, mocker.Mock())

            expected_response = {
                "title": "Validation error.",
                "detail": [f"Title cannot be {ErrorTriggers.SERIALIZER_VALIDATION}"],
                "invalid_params": None,
            }
            assert render_response(response.data) == expected_response
