# Import necessary modules
from django.urls import path
from .views import VendorListCreateAPIView, VendorRetrieveUpdateDestroyAPIView, \
                   PurchaseOrderListCreateAPIView, PurchaseOrderRetrieveUpdateDestroyAPIView, VendorPerformanceAPIView, AcknowledgePurchaseOrderAPIView, UpdatePurchaseOrderStatusAPIView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # Vendor URLs
    path('vendors/', VendorListCreateAPIView.as_view(), name='vendor-list-create'),
    path('vendors/<int:pk>/', VendorRetrieveUpdateDestroyAPIView.as_view(), name='vendor-retrieve-update-destroy'),

    # Purchase Order URLs
    path('purchase_orders/', PurchaseOrderListCreateAPIView.as_view(), name='purchase-order-list-create'),
    path('purchase_orders/<int:pk>/', PurchaseOrderRetrieveUpdateDestroyAPIView.as_view(), name='purchase-order-retrieve-update-destroy'),
    
    path('vendors/<int:pk>/performance/', VendorPerformanceAPIView.as_view(), name='vendor-performance'),
    path('purchase_orders/<int:po_id>/acknowledge/', AcknowledgePurchaseOrderAPIView.as_view(), name='acknowledge_purchase_order'),
    path('purchase_orders/<int:po_id>/status/', UpdatePurchaseOrderStatusAPIView.as_view(), name='update_purchase_order_status'),
    
    # JWT token management endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
]

