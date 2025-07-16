from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

import pytest

from test_app.factories import BookFactory, LibraryFactory, UserFactory
from test_app.models import Book, Library
from test_app.utils import ErrorTriggers

User = get_user_model()


@pytest.fixture
def book():
    author = UserFactory()
    return BookFactory(author=author)


@pytest.fixture
def library():
    return LibraryFactory()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def book_serializer():
    class BookSerializer(serializers.Serializer):
        isbn10 = serializers.CharField()
        pages = serializers.CharField()
        title = serializers.CharField()

        def validate_isbn10(self, isbn10):
            if Book.objects.filter(isbn10=isbn10).exists():
                raise serializers.ValidationError(
                    _(f"Book with isbn10 {isbn10} already exists.")
                )

            return isbn10

        def validate(self, attrs):
            if attrs["title"] == ErrorTriggers.SERIALIZER_VALIDATION.value:
                raise serializers.ValidationError(
                    _(f"Title cannot be {ErrorTriggers.SERIALIZER_VALIDATION}")
                )

            return super().validate(attrs)

    return BookSerializer


@pytest.fixture
def book_model_serializer():
    class BookSerializer(serializers.ModelSerializer):
        author = serializers.SlugRelatedField(
            slug_field="username", queryset=User.objects.only("username")
        )
        libraries = serializers.SlugRelatedField(
            slug_field="name",
            queryset=Library.objects.only("name"),
            many=True,
            required=False,
        )

        class Meta:
            model = Book
            fields = ("author", "edition", "isbn10", "libraries", "pages", "title")

        def create(self, validated_data):
            if validated_data["title"] == ErrorTriggers.SERIALIZER_METHOD.value:
                raise serializers.ValidationError(ErrorTriggers.SERIALIZER_METHOD)

            return Book.objects.create(**validated_data)

        def validate(self, attrs):
            if attrs["title"] == ErrorTriggers.SERIALIZER_VALIDATION.value:
                raise serializers.ValidationError(
                    _(f"Title cannot be {ErrorTriggers.SERIALIZER_VALIDATION}")
                )

            return super().validate(attrs)

    return BookSerializer
