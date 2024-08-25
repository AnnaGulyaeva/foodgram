from favorites.models import BaseUserRecipeModel


class ShoppingList(BaseUserRecipeModel):
    """Модель списка покупок."""

    class Meta:
        """Дополнительные настроки модели."""

        default_related_name = 'shopping_list'
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
