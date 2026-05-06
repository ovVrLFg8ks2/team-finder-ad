from django.core.exceptions import ValidationError

from .constants import GITHUB_WEBSITE


def validate_github_url(value):
    url = value.strip()
    if url and GITHUB_WEBSITE not in url:
        raise ValidationError(f"Ссылка должна вести на {GITHUB_WEBSITE}")
