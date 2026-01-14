from django.urls import path, include
# from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter

from .views import (
    ShopIndexView,
    GroupsListView,
    ProductDetailsView,
    ProductsListView,
    ProductsCreateView,
    ProductsUpdateView,
    ProductsDeleteView,
    ProductsDataExportView,
    ProductViewSet,
    OrdersListView,
    OrderDetailView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
    OrdersExportView,
    UserOrdersExportView,
    OrderViewSet,
    LatestProductsFeed,
    UserOrdersListView,
)

app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)
# routers.register("orders", OrderViewSet)

urlpatterns = [
    # path('', cache_page(60 * 2)(ShopIndexView.as_view()), name='shop_index'),
    path('', ShopIndexView.as_view(), name='shop_index'),
    path('api/', include(routers.urls)),
    path('groups/', GroupsListView.as_view(), name='groups_list'),
    path('products/', ProductsListView.as_view(), name='products_list'),
    path('products/export/', ProductsDataExportView.as_view(), name='products_export'),
    path('products/create/', ProductsCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', ProductDetailsView.as_view(), name='product_details'),
    path('products/<int:pk>/update', ProductsUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/archive', ProductsDeleteView.as_view(), name='product_delete'),
    path('products/latest/feed/', LatestProductsFeed(), name='latest_products_feed'),
    path('orders/', OrdersListView.as_view(), name='orders_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='view_orders'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(), name='orders_update'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),
    path('orders/create', OrderCreateView.as_view(), name='order_create'),
    path('orders/export/', OrdersExportView.as_view(), name='orders_export'),
    path('users/<int:user_id>/orders/', UserOrdersListView.as_view(), name='user_orders_list'),
    path('users/<int:user_id>/orders/export/', UserOrdersExportView.as_view(), name='user_orders_export'),
]