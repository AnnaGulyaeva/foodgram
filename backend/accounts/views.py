from django.shortcuts import get_object_or_404
from rest_framework import (
    filters,
    generics,
    pagination,
    permissions,
    status,
    viewsets
)
from rest_framework.response import Response

from accounts.models import User
from accounts.serializers import (
    AvatarCreateDeleteSerializer,
    SetPasswordSerializer,
    UserCreateSerializer,
    UsersGetListSerializer
)


class UsersViewSet(viewsets.ModelViewSet):
    """Создание пользователя и получение списка пользователей."""

    queryset = User.objects.all()
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if (self.request.method in permissions.SAFE_METHODS):
            return UsersGetListSerializer
        return UserCreateSerializer

    def get_serializer_context(self):
        """Определение контекста сериализатора."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class MeViewSet(generics.RetrieveUpdateAPIView):
    """Получение и изменение данных своей учётной записи."""

    serializer_class = UsersGetListSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Получение объекта пользователя по username."""
        return get_object_or_404(
            User,
            username=self.request.user.get_username()
        )


class AvatarCreateDeleteViewSet(MeViewSet, generics.DestroyAPIView):
    """Добавление и удаление аватара."""

    serializer_class = AvatarCreateDeleteSerializer

    def delete(self, request, *args, **kwargs):
        """Удаление аватара."""
        user = self.get_object()
        user.avatar = None
        user.save(update_fields=['avatar'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class SetPasswordViewSet(generics.UpdateAPIView):
    """Изменение пароля."""

    serializer_class = SetPasswordSerializer

    def post(self, request, *args, **kwargs):
        """Сохранение нового пароля в БД."""
        self.object = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
