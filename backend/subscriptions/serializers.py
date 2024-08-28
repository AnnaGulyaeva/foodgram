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
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        """Дополнительные настроки сериализатора."""

        model = Follow
        fields = (
            'user',
            'following',
            'recipes',
            'recipes_count'
        )
        validators = [
            validate_follower,
            validate_follow
        ]

    def get_recipes(self, obj):
        """Получение списка рецептов."""
        author = obj.following
        recipes = author.recipes.all()
        if 'recipes_limit' in self.context:
            recipes_limit = self.context['recipes_limit']
            if isinstance(recipes_limit, int):
                recipes = recipes[:int(recipes_limit)]
        return RecipeWithoutIngredientsTagsSerializer(
            recipes,
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, obj):
        """Получение количества рецептов."""
        author = obj.following
        print(author.recipes.all().count())
        return author.recipes.all().count()

    def to_representation(self, instance):
        """Изменение возвращаемых данных."""
        representation = super().to_representation(instance)
        print(representation)
        representation.pop('user')
        representation = UsersGetListSerializer(
            instance.following,
            context=self.context
        ).data
        data = super().to_representation(instance)
        representation['recipes_count'] = data['recipes_count']
        representation['recipes'] = data['recipes']
        return representation


class SubscribtionsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели связи пользователя с подпиской."""

    followers = FollowSerializer(
        many=True,
        read_only=True,
        source='follower'
    )

    class Meta:
        """Дополнительные настройки сериализатора."""

        model = User
        fields = ('followers',)

    def to_representation(self, instance):
        """Изменение возвращаемых данных."""
        representation = FollowSerializer(
            instance,
            context=self.context
        ).data
        return representation
