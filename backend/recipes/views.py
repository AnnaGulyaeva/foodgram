import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import (
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
    IngredientRecipe,
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
from shopping_list.constants import (
    PDF_FILENAME,
    PDF_MIN_PAGE_SIZE,
    PDF_PAGE_NAME,
    PDF_START_X,
    PDF_START_Y,
    PDF_STRING_SIZE
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

    @action(detail=False)
    def download_shopping_cart(self, request, format=None):
        """Получение списка покупок."""
        buffer = io.BytesIO()
        self.create_pdf(buffer)
        buffer.seek(0)
        response = FileResponse(
            buffer,
            content_type='application/pdf'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{PDF_FILENAME}"'
        )
        return response

    @action(detail=True, methods=['delete', 'post'])
    def favorite(self, request, pk=None):
        """Добавление и удаление рецепта, избранное."""
        if request.method == 'DELETE':
            user = request.user
            recipe = get_object_or_404(Recipe, pk=pk)
            instance = user.favorites.filter(recipe_id=recipe.id)
            return self.delete_recipe(instance)
        return self.add_recipe(request, pk, FavoriteSerializer)

    @action(detail=True, url_path='get-link')
    def get_short_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = RecipeShortUrlSerializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete', 'post'])
    def shopping_cart(self, request, pk=None):
        """Добавление и удаление рецепта, список покупок."""
        if request.method == 'DELETE':
            user = request.user
            recipe = get_object_or_404(Recipe, pk=pk)
            instance = user.shopping_lists.filter(recipe_id=recipe.id)
            return self.delete_recipe(instance)
        return self.add_recipe(request, pk, ShoppingListSerializer)

    def add_recipe(self, request, recipe_id, serializer):
        """Добавление рецепта."""
        data = request.data
        data['user'] = request.user
        data['recipe'] = get_object_or_404(Recipe, pk=recipe_id)
        serializer = serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, instance):
        """Удаление рецепта."""
        if not instance:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create_pdf(self, response):
        """Создание списка покупок в pdf."""
        page = canvas.Canvas(response, pagesize=letter)
        pdfmetrics.registerFont(TTFont(
            'DejaVuSans',
            'recipes/fonts/djsans/DejaVuSans.ttf')
        )
        page.setFont('DejaVuSans', 12)
        page.drawString(PDF_START_X, PDF_START_Y, PDF_PAGE_NAME)
        ingredient_items = self.get_ingredients().items()
        current_y = PDF_START_Y - PDF_STRING_SIZE
        for ingredient in ingredient_items:
            ingredient = (f'{str(ingredient[0])}: '
                          f'{str(ingredient[1][0])} {str(ingredient[1][1])}')
            if current_y < PDF_MIN_PAGE_SIZE:
                page.showPage()
                page.drawString(PDF_START_X, PDF_START_Y, PDF_PAGE_NAME)
                current_y = PDF_START_Y
            page.drawString(PDF_START_X, current_y, ingredient)
            current_y -= PDF_STRING_SIZE
        page.showPage()
        page.save()

    def get_ingredients(self):
        """Получение ингредиентов."""
        user = self.request.user
        shopping_lists = user.shopping_lists.all()
        recipes = Recipe.objects.filter(
            shopping_lists__in=shopping_lists
        )
        queryset = IngredientRecipe.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredient_id',
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')
        ingredients_cart = {
            item['ingredient__name']:
            [item['total_amount'], item['ingredient__measurement_unit']]
            for item in queryset
        }
        return ingredients_cart


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
