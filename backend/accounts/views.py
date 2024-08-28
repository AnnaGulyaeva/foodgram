from django.shortcuts import get_object_or_404
from rest_framework import (
    filters,
    generics,
    pagination,
    permissions,
    status,
    viewsets
)
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import User
from accounts.serializers import (
    AvatarCreateDeleteSerializer,
    SetPasswordSerializer,
    UserCreateSerializer,
    UsersGetListSerializer
)
from recipes.permissions import IsSafeMethodOrAuthor
from subscriptions.serializers import (
    FollowSerializer,
    SubscribtionsSerializer
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

    @action(
        detail=True,
        methods=['delete', 'post'],
        permission_classes=[permissions.IsAuthenticated, IsSafeMethodOrAuthor]
    )
    def subscribe(self, request, pk=None):
        """Создание и удаление подписки на пользователя."""
        user = request.user
        following = get_object_or_404(User, pk=pk)
        if request.method == 'DELETE':
            instance = user.follower.filter(following_id=following.id)
            if not instance:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.method == 'POST':
            data = request.data
            data['user'] = user
            data['following'] = following
            context = self.get_serializer_context()
            recipes_limit = request.query_params.get('recipes_limit', None)
            if recipes_limit:
                context['recipes_limit'] = recipes_limit
            serializer = FollowSerializer(
                data=data,
                context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def subscriptions(self, request):
        """Получение списка подписок."""
        queryset = request.user.follower.all()
        context = self.get_serializer_context()
        recipes_limit = request.query_params.get('recipes_limit', None)
        page = self.paginate_queryset(queryset)
        if recipes_limit:
            context['recipes_limit'] = recipes_limit
        serializer = SubscribtionsSerializer(
            page,
            many=True,
            context=context
        )
        return self.get_paginated_response(serializer.data)


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
