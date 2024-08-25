from django.urls import include, path
from rest_framework import routers

from accounts.views import (
    AvatarCreateDeleteViewSet,
    MeViewSet,
    SetPasswordViewSet,
    UsersViewSet
)
from subscriptions.views import FollowViewSet

app_name = 'accounts'

router_v1 = routers.DefaultRouter()
router_v1.register('', UsersViewSet, basename='users')

router_subscriptions_v1 = routers.DefaultRouter()
router_subscriptions_v1.register('', FollowViewSet, basename='subscriptions')

router_subscribe_v1 = routers.DefaultRouter()
router_subscribe_v1.register('', FollowViewSet, basename='subscribe')

v1_urls = [
    path('auth/token/', include('djoser.urls.authtoken')),
    path('me/avatar/', AvatarCreateDeleteViewSet.as_view()),
    path('me/', MeViewSet.as_view()),
    path('set_password/', SetPasswordViewSet.as_view()),
    path('<int:id>/subscribe/', include(router_subscribe_v1.urls)),
    path('subscriptions/', include(router_subscriptions_v1.urls)),
    path('', include(router_v1.urls)),
]

urlpatterns = [
    path('', include(v1_urls)),
]
