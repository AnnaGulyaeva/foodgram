from django.apps import AppConfig


class ShoppingListConfig(AppConfig):
    """Настройки приложения shopping_list."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shopping_list'
    verbose_name = "Список покупок"
