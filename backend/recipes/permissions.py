from rest_framework import permissions


class IsSafeMethodOrAuthor(permissions.BasePermission):
    """
    Разрешение на внесение изменений и удаление только для автора.
    """

    def has_object_permission(self, request, view, obj):
        """Проверка разрешений для текущего запроса."""
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
