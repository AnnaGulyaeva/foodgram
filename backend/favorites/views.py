from django.shortcuts import get_object_or_404
from rest_framework import (
    mixins,
    pagination,
    permissions,
    status,
    viewsets
)
from rest_framework.response import Response

from favorites.serializers import FavoriteSerializer
from recipes.models import Recipe
from recipes.permissions import IsAdminOrAuthor


class BaseUserRecipeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Создание, получение списка и удаление рецепта."""

    permission_classes = (
        permissions.IsAuthenticated,
        IsAdminOrAuthor
    )
    pagination_class = pagination.LimitOffsetPagination

    def get_recipe(self):
        """Получение рецепта по id."""
        return get_object_or_404(Recipe, pk=self.kwargs['id'])

    def create(self, request, *args, **kwargs):
        """Добавление рецепта текущим пользователем."""
        data = request.data
        data['user'] = self.request.user
        data['recipe'] = self.get_recipe()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """Удаление рецепта текущим пользователем."""
        recipe = self.get_recipe()
        queryset = self.get_queryset()
        instance = queryset.filter(recipe_id=recipe.id)
        if not instance:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(BaseUserRecipeViewSet):
    """Создание, получение списка и удаление рецепта в избранном."""

    serializer_class = FavoriteSerializer

    def get_queryset(self):
        """Переопределение получаемого списка избранного."""
        user = self.request.user
        return user.favorites.all()
