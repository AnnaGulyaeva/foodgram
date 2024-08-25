from rest_framework import permissions


class IsAdminOrAuthor(permissions.BasePermission):
    """
    Разрешение на внесение изменений и удаление только для автора
    или администратора.
    """

    def has_object_permission(self, request, view, obj):
        """Проверка разрешений для текущего запроса."""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )
