from django.http import HttpResponse

from django.shortcuts import get_list_or_404, get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import (
    permissions,
    views
)

from favorites.views import BaseUserRecipeViewSet
from recipes.models import Ingredient, IngredientRecipe
from recipes.permissions import IsAdminOrAuthor
from shopping_list.constants import (
    PDF_FILENAME,
    PDF_MIN_PAGE_SIZE,
    PDF_PAGE_NAME,
    PDF_START_X,
    PDF_START_Y,
    PDF_STRING_SIZE
)
from shopping_list.serializers import ShoppingListSerializer


class ShoppingListViewSet(BaseUserRecipeViewSet):
    """Создание, получение списка и удаление рецепта в списке покупок."""

    serializer_class = ShoppingListSerializer

    def get_queryset(self):
        """Переопределение получаемого списка покупок."""
        user = self.request.user
        return user.shopping_list.all()


class DownloadShoppingListView(views.APIView):
    """Скачивание списка покупок."""

    permission_classes = (
        permissions.IsAuthenticated,
        IsAdminOrAuthor
    )

    def create_pdf(self, response):
        """Создание списка покупок в pdf."""
        page = canvas.Canvas(response, pagesize=letter)
        pdfmetrics.registerFont(TTFont(
            'DejaVuSans',
            'shopping_list/static/fonts/djsans/DejaVuSans.ttf')
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

    def get(self, request, format=None):
        """Получение списка покупок."""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{PDF_FILENAME}"'
        )
        self.create_pdf(response)
        return response

    def get_queryset(self):
        """Переопределение получаемого списка покупок."""
        user = self.request.user
        return user.shopping_list.all()

    def get_ingredients(self):
        """Получение ингредиентов."""
        ingredients_cart = dict()
        for cart in self.get_queryset():
            ingredients = get_list_or_404(
                IngredientRecipe,
                recipe_id=cart.recipe_id
            )
            for ingredient in ingredients:
                item = get_object_or_404(
                    Ingredient,
                    id=ingredient.ingredient_id
                )
                if item.name in ingredients_cart:
                    ingredients_cart[item.name][0] += ingredient.amount
                    continue
                ingredients_cart[item.name] = [
                    ingredient.amount,
                    item.measurement_unit
                ]
        return ingredients_cart
