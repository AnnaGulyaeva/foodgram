from django.db import models
from django.core.validators import MinValueValidator
from django.urls import reverse

from accounts.models import User
from recipes.constants import (
    COOKING_TIME_MIN_VALUE,
    INGREDIENT_AMOUNT_MIN_VALUE,
    MESUREMENT_UNIT_MAX_LENGTH,
    NAME_MAX_LENGTH,
    RECIPE_MAX_LENGTH,
    SLUG_MAX_LENGTH
)


class NameIngredientTagModel(models.Model):
    """Базовый класс моделей."""

    name = models.CharField(
        'Название',
        max_length=NAME_MAX_LENGTH,
        unique=True,
        db_index=True
    )

    class Meta:
        """Дополнительные настройки модели."""

        abstract = True

    def __str__(self):
        """Возвращает название модели."""
        return self.name


class Ingredient(NameIngredientTagModel):
    """Модель ингредиента."""

    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MESUREMENT_UNIT_MAX_LENGTH
    )

    class Meta:
        """Дополнительные настройки модели."""

        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]
        ordering = ('name',)


class Tag(NameIngredientTagModel):
    """Модель тега."""

    slug = models.SlugField(
        'Слаг',
        max_length=SLUG_MAX_LENGTH
    )

    class Meta:
        """Дополнительные настройки модели."""

        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор публикации'
    )
    name = models.CharField(
        'Название',
        max_length=RECIPE_MAX_LENGTH
    )
    image = models.ImageField(
        'Картинка',
        upload_to='images'
    )
    text = models.TextField(
        verbose_name='Текстовое описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        through='TagRecipe'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=(
            MinValueValidator(COOKING_TIME_MIN_VALUE),
        ),
        error_messages={
            'Проверка':
            'Время приготовления не меньше '
            f'{COOKING_TIME_MIN_VALUE} минуты.'
        }
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        """Дополнительные настройки модели."""

        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        """Возвращает название рецепта."""
        return self.name

    def get_absolute_url(self):
        """Возвращает ссылку на рецепт."""
        return reverse(
            'recipes:recipes-detail',
            args=[self.id]
        ).replace('/recipes', '', 1)

    def get_favorites_count(self):
        """Возвращает количество добавлений в избранное."""
        return self.favorites.count()


class IngredientRecipe(models.Model):
    """Вспомогательная модель для связи ингредиента и рецепта."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество в граммах',
        validators=(
            MinValueValidator(INGREDIENT_AMOUNT_MIN_VALUE),
        ),
        error_messages={
            'Проверка':
            'Количество не меньше '
            f'{INGREDIENT_AMOUNT_MIN_VALUE} грамма.'
        }
    )

    def __str__(self):
        """Возвращает название ингредиента и рецепта."""
        return f'{self.ingredient} {self.recipe}'


class TagRecipe(models.Model):
    """Вспомогательная модель для связи тега и рецепта."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    def __str__(self):
        """Возвращает название тега и рецепта."""
        return f'{self.tag} {self.recipe}'
