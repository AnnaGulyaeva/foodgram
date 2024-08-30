from django.contrib import admin

from recipes.filters import TagFilter
from recipes.models import (
    Ingredient,
    IngredientRecipe,
    Recipe,
    Tag,
    TagRecipe
)

admin.site.empty_value_display = 'Не задано'


class IngredientInline(admin.StackedInline):
    """Интерфейс админ-зоны для отображения постов в столбик."""

    model = IngredientRecipe


class TagInline(admin.StackedInline):
    """Интерфейс админ-зоны для отображения постов в столбик."""

    model = TagRecipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Интерфейс админ-зоны для модели ингредиента."""

    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Интерфейс админ-зоны для модели рецепта."""

    inlines = (
        IngredientInline,
        TagInline
    )
    list_display = (
        'author_tag',
        'get_favorites_count',
        'name',
    )
    search_fields = (
        'author_tag',
        'name',
        'text',
        'cooking_time'
    )
    readonly_fields = (
        'author_tag',
        'get_favorites_count'
    )
    list_filter = (TagFilter,)
    fieldsets = (
        (None, {
            'fields': ('author_tag', 'name')
        }),
        ('Количество добавлений в избранное', {
            'fields': ('get_favorites_count',)
        }),
    )

    def author_tag(self, obj):
        return obj.author.username


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Интерфейс админ-зоны для модели тега."""

    list_display = (
        'name',
        'slug'
    )
    search_fields = ('name',)
