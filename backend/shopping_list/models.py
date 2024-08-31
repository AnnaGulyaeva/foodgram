from favorites.models import BaseUserRecipeModel


class ShoppingList(BaseUserRecipeModel):
    """Модель списка покупок."""

    class Meta(BaseUserRecipeModel.Meta):
        """Дополнительные настроки модели."""

        default_related_name = 'shopping_lists'
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
