from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MerchandiseViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'items', MerchandiseViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
