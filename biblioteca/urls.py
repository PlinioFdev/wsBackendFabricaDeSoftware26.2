from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EstanteViewSet

router = DefaultRouter()
router.register('estantes', EstanteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
