import io

from django.db.models import Sum
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, views

from recipes.models import Recipe, IngredientRecipe
from recipes.permissions import IsSafeMethodOrAuthor
from shopping_list.constants import (
    PDF_FILENAME,
    PDF_MIN_PAGE_SIZE,
    PDF_PAGE_NAME,
    PDF_START_X,
    PDF_START_Y,
    PDF_STRING_SIZE
)


class DownloadShoppingListView(views.APIView):
    """Скачивание списка покупок."""

    permission_classes = (
        permissions.IsAuthenticated,
        IsSafeMethodOrAuthor
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

    def get_queryset(self):
        """Переопределение получаемого списка покупок."""
        user = self.request.user
        return user.shopping_lists.all()

    def get_ingredients(self):
        """Получение ингредиентов."""
        recipes = Recipe.objects.filter(
            shopping_lists__in=self.get_queryset()
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
