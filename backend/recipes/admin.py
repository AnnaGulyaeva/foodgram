from django.contrib import admin

from recipes.models import Ingredient, Recipe, Tag

admin.site.empty_value_display = 'Не задано'


class TagFilter(admin.SimpleListFilter):
    """Фильтрация по тегам."""

    title = 'Теги'
    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        """Получение тегов для отображения в фильтре."""
        tags = Tag.objects.all()
        return [tag.name for tag in tags]

    def queryset(self, request, queryset):
        """Фильтрация по выбранному тегу."""
        if self.value():
            return queryset.filter(tags__name=self.value())


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

    list_display = (
        'author_tag',
        'get_favorites_count',
        'name',
    )
    search_fields = (
        'author_tag',
        'name'
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
