from django.urls import include, path
from rest_framework import routers

from recipes.views import (
    GetRecipeShortUrlViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet
)
from shopping_list.views import DownloadShoppingListView

app_name = 'recipes'

router_v1 = routers.DefaultRouter()
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')

v1_urls = [
    path(
        'recipes/<int:id>/get-link/',
        GetRecipeShortUrlViewSet.as_view(),
        name='short_url'
    ),
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingListView.as_view(),
        name='download_shopping_list'
    ),
    path('', include(router_v1.urls)),
]

urlpatterns = [
    path('', include(v1_urls)),
]
