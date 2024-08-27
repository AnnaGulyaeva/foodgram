from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Настройки приложения accounts."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = "Аккаунты пользователей"
