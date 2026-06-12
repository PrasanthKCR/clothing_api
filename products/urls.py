from django.urls import path
from .views import ProductGridListView, ProductDetailView, BaseMenuView, MenuExpandView

urlpatterns = [
    # 1. Product Listing Grid (Handles filters, sort, limit, pagination via parameters)
    path('products/', ProductGridListView.as_view(), name='product-grid'),

    # 2. Individual Product Details
    path('products/<int:product_id>/', ProductDetailView.as_view(), name='product-detail'),

    # 3. Menus Setup
    path('menu/', BaseMenuView.as_view(), name='all-menus'),
    path('menu/<str:gender>/', BaseMenuView.as_view(), name='gender-menu'),

    # 4. Expanded Sub-menus
    path('menu/<str:gender>/menu-items/', MenuExpandView.as_view(), name='menu-expand'),
]