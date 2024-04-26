from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from test_app.utils import ErrorTriggers


class BookEditionChoices(models.TextChoices):
    FIRST = "first", "First"
    SECOND = "second", "Second"
    THIRD = "third", "Third"


class Book(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="books", on_delete=models.CASCADE
    )
    edition = models.CharField(
        max_length=8,
        choices=BookEditionChoices.choices,
        default=BookEditionChoices.FIRST,
    )
    isbn10 = models.CharField(max_length=13, unique=True)
    pages = models.IntegerField()
    title = models.CharField(max_length=32)

    class Meta:
        constraints = [
            models.CheckConstraint(
                # one page a day keeps the errors away ;)
                name="%(app_label)s_%(class)s_pages_lte_360",
                check=models.Q(pages__lte=360),
                # flake8: noqa E501
                # ! this is not available for Django < 4.1
                # ! handle constraint errors as you wish
                # ! error message would look like: "Constraint “test_app_book_pages_lte_360” is violated."
                violation_error_message="Pages cannot be more than 360.",
            )
        ]

    def clean(self):
        super().clean()

        if self.title == ErrorTriggers.MODEL_VALIDATION.value:
            raise ValidationError(ErrorTriggers.MODEL_VALIDATION)

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)


class Library(models.Model):
    books = models.ManyToManyField(Book)
    name = models.CharField(max_length=32)
