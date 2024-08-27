from django.core.exceptions import ValidationError

from accounts.constants import USERNAME_RESERVED


def username_validator(username):
    """Проверка корректности username."""
    if username == USERNAME_RESERVED:
        raise ValidationError(
            'Выберете другое имя пользователя!'
        )
