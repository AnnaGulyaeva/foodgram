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
    recipe_info = serializers.SerializerMethodField()

    class Meta:
        """Дополнительные настроки сериализатора."""

        fields = (
            'user',
            'recipe',
            'recipe_info'
        )

    def get_recipe_info(self, obj):
        """"Получение информации о рецепте."""
        return RecipeWithoutIngredientsTagsSerializer(
            obj.recipe).data

    def to_representation(self, instance):
        """Изменение возвращаемых данных."""
        representation = super().to_representation(instance)
        representation.pop('user')
        representation.pop('recipe')
        representation['id'] = representation['recipe_info']['id']
        representation['name'] = representation['recipe_info']['name']
        representation['image'] = representation['recipe_info']['image']
        representation['cooking_time'] = (
            representation['recipe_info']['cooking_time']
        )
        representation.pop('recipe_info')
        return representation


class FavoriteSerializer(BaseUserRecipeSerializer):
    """Сериализатор для избранного."""

    class Meta:
        """Дополнительные настроки сериализатора."""

        model = Favorite
        fields = '__all__'

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
