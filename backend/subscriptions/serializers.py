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

    class Meta:
        """Дополнительные настроки сериализатора."""

        model = Follow
        fields = (
            'user',
            'following'
        )
        validators = [
            validate_follower,
            validate_follow
        ]

    def to_representation(self, instance):
        """Изменение возвращаемых данных."""
        return SubscribtionsSerializer(
            instance.following,
            context=self.context
        ).data


class SubscribtionsSerializer(UsersGetListSerializer):
    """Сериализатор для модели связи пользователя с подпиской."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(UsersGetListSerializer.Meta):
        """Дополнительные настройки сериализатора."""

        fields = (
            UsersGetListSerializer.Meta.fields
            + ['recipes_count', 'recipes']
        )

    def get_recipes(self, obj):
        """Получение списка рецептов."""
        recipes = obj.recipes.all()
        context = self.context
        if 'request' in context:
            query_params = self.context.get('request').query_params
            recipes_limit = query_params.get('recipes_limit')
            if recipes_limit and recipes_limit.isdigit():
                recipes = recipes[:int(recipes_limit)]
        return RecipeWithoutIngredientsTagsSerializer(
            recipes,
            many=True,
            context=self.context
        ).data
