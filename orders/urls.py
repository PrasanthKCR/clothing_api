from django.urls import path
from .views import PlaceOrderView, OrderHistoryView, OrderDetailsView, PaymentStatusView

urlpatterns = [
    path('place-order/', PlaceOrderView.as_view(), name='place-order'),
    path('order-history/', OrderHistoryView.as_view(), name='order-history'),
    path('<int:order_id>/', OrderDetailsView.as_view(), name='order-details'),
    path('payment-status/', PaymentStatusView.as_view(), name='payment-status'),
]