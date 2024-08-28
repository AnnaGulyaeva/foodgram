from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    generics,
    pagination,
    permissions,
    status,
    viewsets
)
from rest_framework.decorators import action
from rest_framework.response import Response

from favorites.serializers import FavoriteSerializer
from recipes.filters import RecipeFilter
from recipes.models import (
    Ingredient,
    Recipe,
    Tag
)
from recipes.permissions import IsSafeMethodOrAuthor
from recipes.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeShortUrlSerializer,
    TagSerializer
)
from shopping_list.serializers import ShoppingListSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Выполнение CRUD-операций с моделью Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsSafeMethodOrAuthor,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(detail=True, methods=['delete', 'post'])
    def favorite(self, request, pk=None):
        """Добавление и удаление рецепта, избранное."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'DELETE':
            instance = user.favorites.filter(recipe_id=recipe.id)
            if not instance:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.method == 'POST':
            data = request.data
            data['user'] = user
            data['recipe'] = recipe
            serializer = FavoriteSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete', 'post'])
    def shopping_cart(self, request, pk=None):
        """Добавление и удаление рецепта, список покупок."""
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'DELETE':
            instance = user.shopping_lists.filter(recipe_id=recipe.id)
            if not instance:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.method == 'POST':
            data = request.data
            data['user'] = user
            data['recipe'] = recipe
            serializer = ShoppingListSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetRecipeShortUrlViewSet(generics.RetrieveAPIView):
    """Получение короткой ссылки на рецепт."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeShortUrlSerializer
    pagination_class = None

    def get_object(self):
        """Получение объекта рецепта."""
        return get_object_or_404(Recipe, id=self.kwargs['id'])


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ответ на запрос ингредиента или списка ингредиентов."""

    permission_classes = (permissions.AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', )
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Ответ на запрос тега или списка тегов."""

    permission_classes = (permissions.AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
