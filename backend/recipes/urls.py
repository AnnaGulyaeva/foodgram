from django.urls import include, path
from rest_framework import routers

from favorites.views import FavoriteViewSet
from recipes.views import (
    GetRecipeShortUrlViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet
)
from shopping_list.views import (
    DownloadShoppingListView,
    ShoppingListViewSet
)

app_name = 'recipes'

router_v1 = routers.DefaultRouter()
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')

router_favorites_v1 = routers.DefaultRouter()
router_favorites_v1.register('', FavoriteViewSet, basename='favorites')

router_shopping_cart_v1 = routers.DefaultRouter()
router_shopping_cart_v1.register(
    '',
    ShoppingListViewSet,
    basename='shopping_cart'
)

router_short_url_v1 = routers.DefaultRouter()
router_short_url_v1.register(
    '',
    GetRecipeShortUrlViewSet,
    basename='short_url'
)

recipe_urls = [
    path('favorite/', include(router_favorites_v1.urls)),
    path(
        'get-link/',
        GetRecipeShortUrlViewSet.as_view(),
        name='short_url'
    ),
    path('shopping_cart/', include(router_shopping_cart_v1.urls)),
]

v1_urls = [
    path('recipes/<int:id>/', include(recipe_urls)),
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
