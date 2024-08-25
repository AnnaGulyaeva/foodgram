from rest_framework import serializers

from accounts.models import User
from accounts.serializers import UsersGetListSerializer
from recipes.serializers import RecipeWithoutIngredientsTagsSerializer
from subscriptions.models import Follow
from subscriptions.validators import (
    validate_follow,
    validate_follower
)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели связи пользователя с подпиской."""

    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        required=True
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        required=True
    )
    following_info = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        """Дополнительные настроки сериализатора."""

        model = Follow
        fields = (
            'user',
            'following',
            'following_info',
            'recipes',
            'recipes_count'
        )
        validators = [
            validate_follower,
            validate_follow
        ]

    def get_following_info(self, obj):
        """Получение информации об авторе рецептов."""
        return UsersGetListSerializer(
            obj.following,
            context=self.context
        ).data

    def get_recipes(self, obj):
        """Получение списка рецептов."""
        author = obj.following
        if 'recipes_limit' in self.context:
            recipes_limit = int(self.context['recipes_limit'])
            recipes = author.recipes.all()[:recipes_limit]
        else:
            recipes = author.recipes.all()
        return RecipeWithoutIngredientsTagsSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """Получение количества рецептов."""
        author = obj.following
        return author.recipes.all().count()

    def to_representation(self, instance):
        """Изменение возвращаемых данных."""
        representation = super().to_representation(instance)
        following_info = representation['following_info']
        recipes = representation['recipes']
        recipes_count = representation['recipes_count']
        representation.pop('following_info')
        representation.pop('following')
        representation.pop('recipes')
        representation.pop('recipes_count')
        representation.pop('user')
        representation['following'] = following_info
        representation['recipes_count'] = recipes_count
        representation['recipes'] = recipes
        return representation
