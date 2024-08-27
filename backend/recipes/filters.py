import django_filters
from django.contrib import admin

from recipes.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    """Класс для фильтрации возвращаемого списка рецептов."""

    author = django_filters.CharFilter(field_name='author__id')
    tags = django_filters.CharFilter(
        field_name='tags__slug',
        method='filter_by_tags'
    )

    class Meta:
        """Дополнительные настроки фильтра."""

        model = Recipe
        fields = ['name', 'tags']

    def filter_by_tags(self, queryset, name, value):
        """Фильтрация по нескольким тегам."""
        request_tags = self.request.GET.getlist('tags')
        recipes = queryset.filter(tags__slug__in=request_tags)
        return recipes.distinct()


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
