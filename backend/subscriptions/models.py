from django.db import models

from accounts.models import User


class Follow(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        """Дополнительные настроки модели."""

        default_related_name = 'follows'
        verbose_name = 'подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='check_follower_not_following',
            )
        ]

    def __str__(self):
        """Возвращает username подписчика и автора."""
        return (
            f'Подписчик: {self.user.get_username()} '
            f'Автор: {self.following.get_username()}'
        )
