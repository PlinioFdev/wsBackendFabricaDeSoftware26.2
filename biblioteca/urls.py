from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EstanteViewSet, LivroViewSet

router = DefaultRouter()
router.register('estantes', EstanteViewSet)
router.register('livros', LivroViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
