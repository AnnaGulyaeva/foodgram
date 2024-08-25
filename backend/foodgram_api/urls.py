from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

app_name = 'foodgram_api'

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/', include('accounts.urls', namespace='accounts')),
    path('', include('recipes.urls', namespace='recipes'))
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
