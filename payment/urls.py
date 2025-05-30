from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, MembershipPaymentViewSet, NotificationViewSet, FeedbackViewSet
from .mpesa_views import MpesaTransactionViewSet, mpesa_callback

router = DefaultRouter()
router.register(r'payments', PaymentViewSet)
router.register(r'membership-payments', MembershipPaymentViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'feedback', FeedbackViewSet)
router.register(r'mpesa', MpesaTransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('mpesa/callback/', mpesa_callback, name='mpesa-callback'),
]
