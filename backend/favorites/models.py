from django.db import models

from accounts.models import User
from recipes.models import Recipe


class BaseUserRecipeModel(models.Model):
    """Базовый класс для модели связи пользователя с рецептом."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        """Дополнительные настройки модели."""

        abstract = True

    def __str__(self):
        """Возвращает username пользователя и name рецепта."""
        return (
            f'Подписчик: {self.user.get_username()} '
            f'Рецепт: {self.recipe.name}'
        )


class Favorite(BaseUserRecipeModel):
    """Модель избранного."""

    class Meta:
        """Дополнительные настроки модели."""

        default_related_name = 'favorites'
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранные'
        ordering = ('recipe__name',)
