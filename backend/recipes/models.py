from django.db import models
from django.core.validators import MinValueValidator

from accounts.models import User
from recipes.constants import (
    COOCKING_TIME_MIN_VALUE,
    INGREDIENT_MAX_LENGTH,
    MESUREMENT_UNIT_MAX_LENGTH,
    NAME_MAX_LENGTH,
    SLUG_MAX_LENGTH,
    TAG_MAX_LENGTH,
    TEXT_MAX_LENGTH
)


class BaseModel(models.Model):
    """Базовый класс моделей."""

    class Meta:
        """Дополнительные настройки модели."""

        abstract = True

    def __str__(self):
        """Возвращает название модели."""
        return self.name


class Ingredient(BaseModel):
    """Модель ингридиента."""

    name = models.CharField(
        'Название',
        max_length=INGREDIENT_MAX_LENGTH,
        unique=True,
        db_index=True
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MESUREMENT_UNIT_MAX_LENGTH
    )

    class Meta:
        """Дополнительные настройки модели."""

        verbose_name = 'ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)


class Tag(BaseModel):
    """Модель тега."""

    name = models.CharField(
        'Название',
        max_length=TAG_MAX_LENGTH,
        unique=True,
        db_index=True
    )
    slug = models.SlugField(
        'Слаг',
        max_length=SLUG_MAX_LENGTH,
        null=True,
        blank=True
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
        max_length=NAME_MAX_LENGTH
    )
    picture = models.ImageField(
        'Картинка',
        upload_to='pictures'
    )
    description = models.TextField(
        verbose_name='Текстовое описание',
        max_length=TEXT_MAX_LENGTH
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='ingredients',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='tags'
    )
    coocking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=(
            MinValueValidator(COOCKING_TIME_MIN_VALUE),
        ),
        error_messages={'Проверка': 'Время приготовления не меньше 1 минуты.'}
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        """Дополнительные настройки модели."""

        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-pub_date',)

    def __str__(self):
        """Возвращает название произведения."""
        return self.name
