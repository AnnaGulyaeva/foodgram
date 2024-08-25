from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
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

from recipes.filters import RecipeFilter
from recipes.models import (
    Ingredient,
    Recipe,
    Tag
)
from recipes.permissions import IsAdminOrAuthor
from recipes.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeShortUrlSerializer,
    TagSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    """Выполнение CRUD-операций с моделью Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminOrAuthor,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def list(self, request, format=None):
        is_favorited = request.query_params.get('is_favorited', None)
        queryset = self.filter_queryset(self.get_queryset())
        serializer = RecipeSerializer(
            queryset,
            many=True,
            context=self.get_serializer_context()
        )
        is_favorited = request.query_params.get('is_favorited', None)
        if is_favorited:
            for data in serializer.data:
                if bool(data['is_favorited']) != bool(is_favorited):
                    queryset = queryset.exclude(id=data['id'])
        is_in_shopping_cart = request.query_params.get(
            'is_in_shopping_cart', None
        )
        if is_in_shopping_cart:
            for data in serializer.data:
                if bool(data['is_in_shopping_cart']) != bool(is_in_shopping_cart):
                    queryset = queryset.exclude(id=data['id'])
        page = self.paginate_queryset(queryset)
        serializer = RecipeSerializer(
            page,
            many=True,
            context=self.get_serializer_context()
        )
        return self.get_paginated_response(serializer.data)

    def create(self, request):
        """Создание объекта нового пользователя в БД."""
        data = self.get_correct_data(request.data.copy())
        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = self.get_correct_data(request.data.copy())
        serializer = self.get_serializer(
            instance,
            data=data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_correct_data(self, request_data):
        if 'ingredients' not in request_data:
            return None
        if 'tags' not in request_data:
            return None
        ingredients = request_data['ingredients']
        if not ingredients:
            return None
        if not 'tags':
            return None
        ingredients_id = []
        ingredients_amount = []
        for ingredient in ingredients:
            ingredients_id.append(ingredient['id'])
            ingredients_amount.append(ingredient['amount'])
        request_data['ingredients'] = ingredients_id
        request_data['amounts'] = ingredients_amount
        return request_data

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class GetRecipeShortUrlViewSet(generics.RetrieveAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeShortUrlSerializer
    pagination_class = None

    def get_object(self):
        """Получение объекта жанра."""
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
