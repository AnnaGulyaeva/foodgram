from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User

admin.site.empty_value_display = 'Не задано'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Интерфейс админ-зоны для модели пользователя."""

    search_fields = (
        'email',
        'username'
    )
    list_filter = (
        'email',
        'username'
    )
    list_display_links = ('username',)
