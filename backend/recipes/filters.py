import django_filters
from django.contrib import admin

from recipes.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    """Класс для фильтрации возвращаемого списка рецептов."""

    tags = django_filters.MultipleChoiceFilter(
        field_name='tags__slug',
        choices=Tag.objects.values_list('slug', 'slug')
    )
    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        """Дополнительные настроки фильтра."""

        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация по избранному."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация по списку покупок."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_lists__user=self.request.user)
        return queryset


class TagFilter(admin.SimpleListFilter):
    """Фильтрация по тегам."""

    title = 'Теги'
    parameter_name = 'tags'

    def lookups(self, request, model_admin):
        """Получение тегов для отображения в фильтре."""
        tags = Tag.objects.all()
        return [(tag.id, tag.name) for tag in tags]

    def queryset(self, request, queryset):
        """Фильтрация по выбранному тегу."""
        if self.value():
            return queryset.filter(tags__name=self.value())
        return queryset
