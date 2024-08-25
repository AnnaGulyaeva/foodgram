from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from accounts.serializers import UsersGetListSerializer
from favorites.models import Favorite
from foodgram.images import Base64ImageField
from recipes.constants import TEXT_MAX_LENGTH
from recipes.models import (
    Ingredient,
    IngredientRecipe,
    Recipe,
    Tag,
    TagRecipe
)
from shopping_list.models import ShoppingList


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        """Дополнительные настройки сериализатора."""

        fields = '__all__'
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        """Дополнительные настройки сериализатора."""

        fields = '__all__'
        model = Tag


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецепта."""

    image = Base64ImageField(required=True)
    image_url = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )

    def get_image_url(self, obj):
        """Получение ссылки на изображение."""
        if obj.image:
            return obj.image.url
        return 'None'


class RecipeSerializer(BaseRecipeSerializer):
    """Сериализатор для модели Post."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    author_info = serializers.SerializerMethodField()
    text = serializers.CharField(
        max_length=TEXT_MAX_LENGTH,
        source='description'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    tags_info = serializers.SerializerMethodField()
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )
    ingredients_info = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Дополнительные настроки сериализатора."""

        model = Recipe
        fields = (
            'id',
            'tags',
            'tags_info',
            'author',
            'author_info',
            'ingredients',
            'ingredients_info',
            'name',
            'image',
            'image_url',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_author_info(self, obj):
        """Получение информации об авторе рецептов."""
        return UsersGetListSerializer(
            obj.author,
            context=self.context
        ).data

    def get_amount(self, recipe_id, ingredient):
        """Получение количества ингредиента."""
        return get_object_or_404(
            IngredientRecipe,
            ingredient=ingredient,
            recipe_id=recipe_id
        ).amount

    def get_ingredients_info(self, obj):
        """Получение ингрудиентов."""
        return IngredientSerializer(
            obj.ingredients.all(),
            many=True
        ).data

    def get_is_favorited(self, obj):
        """Проверка: находится ли рецепт в избранном."""
        if Favorite.objects.filter(
            user_id=self.context['request'].user.id,
            recipe_id=obj.id
        ):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        """Проверка: находится ли рецепт в списке покупок."""
        if ShoppingList.objects.filter(
            user_id=self.context['request'].user.id,
            recipe_id=obj.id
        ):
            return True
        return False

    def get_tags_info(self, obj):
        """Получение тегов."""
        return TagSerializer(
            obj.tags.all(),
            many=True
        ).data

    def validate_ingredients(self, ingredients):
        """Проверка корректности данных для ингридиентов."""
        if not ingredients:
            raise ValidationError('Отсутствуют ингредиенты!')
        amounts = self.initial_data['amounts']
        safe_ingredients = []
        for i, ingredient in enumerate(ingredients):
            current_ingredient = get_object_or_404(
                Ingredient,
                name=ingredient
            )
            if current_ingredient in safe_ingredients:
                raise ValidationError('Ингредиенты повторяются!')
            safe_ingredients.append(current_ingredient)
            if int(amounts[i]) < 1:
                raise ValidationError(
                    f'Количество ингредиента {ingredient} указано неверно!'
                )
        return ingredients

    def validate_tags(self, tags):
        """Проверка корректности данных для тегов."""
        if not tags:
            raise ValidationError('Отсутствуют теги!')
        safe_tags = []
        for tag in tags:
            current_tag = get_object_or_404(Tag, name=tag)
            if current_tag in safe_tags:
                raise ValidationError('Теги повторяются!')
            safe_tags.append(current_tag)
        return tags

    def create(self, validated_data):
        """Добавление рецепта и связей с ним тегов и рецептов в БД."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        amounts = self.initial_data['amounts']
        recipe = Recipe.objects.create(**validated_data)
        for i, ingredient in enumerate(ingredients):
            current_ingredient = Ingredient.objects.get(name=ingredient)
            IngredientRecipe.objects.create(
                ingredient=current_ingredient,
                recipe_id=recipe.id,
                amount=amounts[i]
            )
        for tag in tags:
            current_tag = Tag.objects.get(name=tag)
            TagRecipe.objects.create(
                recipe_id=recipe.id,
                tag=current_tag
            )
        return recipe

    def to_representation(self, instance):
        """Изменение возвращаемых данных."""
        representation = super().to_representation(instance)
        name = representation['name']
        text = representation['text']
        cooking_time = representation['cooking_time']
        representation.pop('name')
        representation.pop('text')
        representation.pop('cooking_time')
        representation['author'] = representation['author_info']
        representation.pop('author_info')
        representation['tags'] = representation['tags_info']
        representation.pop('tags_info')
        for ingredient in representation['ingredients_info']:
            ingredient['amount'] = self.get_amount(
                representation['id'],
                ingredient['id']
            )
        representation['ingredients'] = representation['ingredients_info']
        representation.pop('ingredients_info')
        representation['name'] = name
        representation['image'] = representation['image_url']
        representation.pop('image_url')
        representation['text'] = text
        representation['cooking_time'] = cooking_time
        return representation


class RecipeShortUrlSerializer(serializers.HyperlinkedModelSerializer):
    """Сериализатор для получения короткой ссылки рецепта."""

    short_link = serializers.SerializerMethodField()

    class Meta:
        """Дополнительные настроки сериализатора."""

        model = Recipe
        fields = ('short_link',)

    def get_short_link(self, obj):
        """Получение короткой ссылки рецепта."""
        request = self.context.get('request')
        return request.build_absolute_uri(obj.get_absolute_url())

    def to_representation(self, instance):
        """Изменение возвращаемых данных."""
        representation = super().to_representation(instance)
        representation['short-link'] = representation['short_link']
        representation.pop('short_link')
        return representation


class RecipeWithoutIngredientsTagsSerializer(BaseRecipeSerializer):
    """Сериализатор для модели Post."""

    class Meta:
        """Дополнительные настроки сериализатора."""

        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'image_url',
            'cooking_time'
        )

    def to_representation(self, instance):
        """Изменение возвращаемых данных."""
        representation = super().to_representation(instance)
        cooking_time = representation['cooking_time']
        representation.pop('cooking_time')
        representation['image'] = representation['image_url']
        representation.pop('image_url')
        representation['cooking_time'] = cooking_time
        return representation
