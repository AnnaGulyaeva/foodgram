from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User

admin.site.empty_value_display = 'Не задано'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Интерфейс админ-зоны для модели пользователя."""

    list_display = (
        'username',
        'email',
        'recipes_count',
        'following_count'
    )
    search_fields = (
        'email',
        'username'
    )
    list_filter = (
        'email',
        'username'
    )
    list_display_links = ('username',)

    def recipes_count(self, obj):
        """Возвращает количество рецептов."""
        return obj.recipes.count()
    recipes_count.short_description = 'Количество рецептов'

    def following_count(self, obj):
        """Возвращает количество подписчиков."""
        return obj.following.count()
    following_count.short_description = 'Количество подписчиков'
