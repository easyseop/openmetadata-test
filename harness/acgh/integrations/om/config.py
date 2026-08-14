"""OpenMetadata naming and registration conventions."""

from __future__ import annotations

import re

CUSTOMIZATION_ID_PATTERN = re.compile(r"^BANK-OM-[0-9]{3,}$")
REGISTRATION_PREFIX = "om-temp-"


def registration_relative_path(version: str) -> str:
    return f"harness/registrations/{REGISTRATION_PREFIX}{version}"
