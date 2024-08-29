from django.shortcuts import get_object_or_404
from rest_framework import serializers

from accounts.serializers import UsersGetListSerializer
from foodgram_api.fields import Base64ImageField
from recipes.constants import INGREDIENT_AMOUNT_MIN_VALUE
from recipes.models import (
    Ingredient,
    IngredientRecipe,
    Recipe,
    Tag
)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        """Дополнительные настройки сериализатора."""

        fields = '__all__'
        model = Ingredient


class IngredientAmountSerializer(serializers.Serializer):
    """Сериализатор для ингридиентов с количеством."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        """Дополнительные настройки сериализатора."""

        fields = '__all__'
        model = Tag


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для модели рецепта."""

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
    """Сериализатор для модели рецепта."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientAmountSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Дополнительные настроки сериализатора."""

        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'image_url',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_amount(self, recipe_id, ingredient):
        """Получение количества ингредиента."""
        return get_object_or_404(
            IngredientRecipe,
            ingredient=ingredient,
            recipe_id=recipe_id
        ).amount

    def get_is_favorited(self, obj):
        """Проверка: находится ли рецепт в избранном."""
        return obj.favorites.filter(
            user_id=self.context['request'].user.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка: находится ли рецепт в списке покупок."""
        return obj.shopping_lists.filter(
            user_id=self.context['request'].user.id
        ).exists()

    def validate(self, attrs):
        """Проверка корректности данных для ингридиентов."""
        if 'ingredients' not in attrs:
            raise serializers.ValidationError('Отсутствуют ингредиенты!')
        ingredients = attrs['ingredients']
        if not ingredients:
            raise serializers.ValidationError('Отсутствуют ингредиенты!')
        safe_ingredients = []
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient,
                id=ingredient['id'].id
            )
            if current_ingredient in safe_ingredients:
                raise serializers.ValidationError('Ингредиенты повторяются!')
            safe_ingredients.append(current_ingredient)
            if int(ingredient['amount']) < INGREDIENT_AMOUNT_MIN_VALUE:
                raise serializers.ValidationError(
                    f'Количество ингредиента {ingredient} указано неверно!'
                )
        if 'tags' not in attrs:
            raise serializers.ValidationError('Отсутствуют теги!')
        tags = attrs['tags']
        if not tags:
            raise serializers.ValidationError('Отсутствуют теги!')
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError('Теги повторяются!')
        return attrs

    def add_ingredients(self, ingredients, recipe):
        """Добавление и обновление ингредиентов рецепта в БД."""
        ingredient_recipes = [
            IngredientRecipe(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=int(ingredient['amount'])
            )
            for ingredient in ingredients
        ]
        IngredientRecipe.objects.bulk_create(ingredient_recipes)

    def create(self, validated_data):
        """Добавление рецепта и связей с ним тегов и рецептов в БД."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """Изменение рецепта и связей с ним тегов и рецептов в БД."""
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        instance.ingredients.clear()
        self.add_ingredients(validated_data.pop('ingredients'), instance)
        instance = super().update(instance, validated_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Изменение возвращаемых данных."""
        representation = RecipeReadSerializer(instance).data
        representation['author'] = UsersGetListSerializer(
            instance.author,
            context=self.context
        ).data
        representation['tags'] = TagSerializer(
            instance.tags.all(),
            many=True
        ).data
        representation['ingredients'] = IngredientSerializer(
            instance.ingredients.all(),
            many=True
        ).data
        for ingredient in representation['ingredients']:
            ingredient['amount'] = self.get_amount(
                representation['id'],
                ingredient['id']
            )
        representation['is_favorited'] = self.get_is_favorited(instance)
        representation['is_in_shopping_cart'] = (
            self.get_is_in_shopping_cart(instance)
        )
        return representation


class RecipeReadSerializer(BaseRecipeSerializer):
    """Сериализатор для чтения модели рецепта."""

    class Meta:
        """Дополнительные настроки сериализатора."""

        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'image_url',
            'name',
            'text',
            'cooking_time'
        )

    def to_representation(self, instance):
        """Изменение возвращаемых данных."""
        representation = super().to_representation(instance)
        representation['image'] = representation.pop('image_url')
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
        representation['short-link'] = representation.pop('short_link')
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
        representation['image'] = representation['image_url']
        representation.pop('image_url')
        return representation
