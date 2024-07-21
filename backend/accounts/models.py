from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.constants import (
    EMAIL_MAX_LENGTH,
    NAME_MAX_LENGTH,
    TEXT_REPRESENTATION_COUNT
)


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        'Почтовый адрес',
        max_length=EMAIL_MAX_LENGTH,
        unique=True
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=NAME_MAX_LENGTH,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=NAME_MAX_LENGTH,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=NAME_MAX_LENGTH
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars',
        blank=True,
        null=True
    )

    class Meta:
        """Дополнительные настройки модели."""

        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_user'
            )
        ]
        ordering = ['username']

    def __str__(self):
        """Возвращает имя пользователя."""
        return self.username[:TEXT_REPRESENTATION_COUNT]
