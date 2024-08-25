import django_filters

from recipes.models import Recipe


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
