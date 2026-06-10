"""
Settings for the DRF Simple API Errors package.
This module defines the default settings and user settings for the package.
"""

from django.conf import settings
from rest_framework.settings import APISettings

USER_SETTINGS = getattr(settings, "DRF_SIMPLE_API_ERRORS", {})

DEFAULTS = {
    "CAMELIZE": False,
    "EXTRA_HANDLERS": [],
    "FIELDS_SEPARATOR": ".",
    "SPECTACULAR_ERROR_STATUS_CODES": {
        "400": "Validation error",
        "401": "Authentication error",
        "403": "Permission denied",
        "404": "Not found",
        "500": "Server error",
    },
}

# List of settings that may be in string import notation
# e.g. when defined in settings.py as "app.module.class_name"
IMPORT_STRINGS = []

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
