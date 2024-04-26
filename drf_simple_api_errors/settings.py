from django.conf import settings
from rest_framework.settings import APISettings

USER_SETTINGS = getattr(settings, "DRF_SIMPLE_API_ERRORS", {})

DEFAULTS = {
    "CAMELIZE": False,
    "EXTRA_HANDLERS": [],
    "FIELDS_SEPARATOR": ".",
}

# List of settings that may be in string import notation
IMPORT_STRINGS = ("EXTRA_HANDLERS", "CAMELIZE")

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
