from rest_framework import serializers

from accounts.models import User
from favorites.models import Favorite
from recipes.models import Recipe
from recipes.serializers import RecipeWithoutIngredientsTagsSerializer


class BaseUserRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели связи пользователя с рецептом."""

    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        required=True
    )
    recipe = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Recipe.objects.all(),
        required=True
    )

    class Meta:
        """Дополнительные настроки сериализатора."""

        fields = (
            'user',
            'recipe'
        )

    def to_representation(self, instance):
        """Изменение возвращаемых данных."""
        return RecipeWithoutIngredientsTagsSerializer(
            instance.recipe
        ).data


class FavoriteSerializer(BaseUserRecipeSerializer):
    """Сериализатор для избранного."""

    class Meta(BaseUserRecipeSerializer.Meta):
        """Дополнительные настроки сериализатора."""

        model = Favorite

    def validate(self, data):
        """Проверка корректности данных."""
        user = data['user']
        recipe = data['recipe']
        if Favorite.objects.filter(
            user_id=user.id,
            recipe_id=recipe.id
        ):
            raise serializers.ValidationError(
                'Рецепт уже был добавлен в избранное!'
            )
        return data
