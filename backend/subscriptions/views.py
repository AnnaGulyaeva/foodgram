from django.shortcuts import get_object_or_404
from rest_framework import (
    mixins,
    pagination,
    permissions,
    status,
    viewsets
)
from rest_framework.response import Response

from accounts.models import User
from recipes.permissions import IsAdminOrAuthor
from subscriptions.models import Follow
from subscriptions.serializers import FollowSerializer


class FollowViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Выполнение CRUD-операций с моделью Follow."""

    serializer_class = FollowSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsAdminOrAuthor
    )
    pagination_class = pagination.LimitOffsetPagination

    def get_following(self):
        """Получение автора рецепта по id."""
        return get_object_or_404(User, pk=self.kwargs['id'])

    def get_serializer_context(self):
        """Определение контекста сериализатора."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        """Переопределение получаемого списка подписок пользователя."""
        return Follow.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Добавление подписки текущим пользователем."""
        data = request.data
        data['user'] = self.request.user
        data['following'] = self.get_following()
        context = self.get_serializer_context()
        recipes_limit = request.query_params.get('recipes_limit', None)
        if recipes_limit:
            context['recipes_limit'] = recipes_limit
        serializer = self.get_serializer(
            data=data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """Удаление подписки текущим пользователем."""
        following = self.get_following()
        queryset = self.get_queryset()
        instance = queryset.filter(following_id=following.id)
        if not instance:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, format=None):
        """Получение списка подписок текущего пользователя."""
        queryset = self.get_queryset()
        context = self.get_serializer_context()
        recipes_limit = request.query_params.get('recipes_limit', None)
        page = self.paginate_queryset(queryset)
        if recipes_limit:
            context['recipes_limit'] = recipes_limit
        serializer = self.get_serializer(
            page,
            many=True,
            context=context
        )
        return self.get_paginated_response(serializer.data)
