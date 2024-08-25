from rest_framework import serializers

from favorites.serializers import BaseUserRecipeSerializer
from shopping_list.models import ShoppingList


class ShoppingListSerializer(BaseUserRecipeSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        """Дополнительные настроки сериализатора."""

        model = ShoppingList
        fields = '__all__'

    def validate(self, data):
        """Проверка корректности данных."""
        user = data['user']
        recipe = data['recipe']
        if ShoppingList.objects.filter(
            user_id=user.id,
            recipe_id=recipe.id
        ):
            raise serializers.ValidationError(
                'Рецепт уже был добавлен в список покупок!'
            )
        return data
