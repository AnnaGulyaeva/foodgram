from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from rest_framework import routers

from accounts.views import UsersViewSet

router_v1 = routers.DefaultRouter()
router_v1.register('', UsersViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
    path('api/', include('foodgram_api.urls', namespace='foodgram_api')),
    path('user/<int:id>/', include(router_v1.urls)),
    path('users/', include('accounts.urls', namespace='accounts')),
    path('recipes/', include('recipes.urls', namespace='recipes')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
