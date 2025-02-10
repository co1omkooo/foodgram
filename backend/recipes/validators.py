import re

from django.core.exceptions import ValidationError


def validate_slug(slug):
    """Проверка слага."""
    if not re.fullmatch(r'^[-a-zA-Z0-9_]+$', slug):
        raise ValidationError(
            'Слаг содержит недопустимые символы.'
        )
    return slug
