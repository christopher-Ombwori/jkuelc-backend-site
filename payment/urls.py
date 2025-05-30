from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, MembershipPaymentViewSet, NotificationViewSet, FeedbackViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet)
router.register(r'membership-payments', MembershipPaymentViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'feedback', FeedbackViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
