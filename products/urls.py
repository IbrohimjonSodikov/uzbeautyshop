from django.urls import path
from .views import ProductDetailView, AllProductsList, checkout, add_to_cart, add_to_favorites, cart_view, favorites_view, remove_from_cart, remove_from_favorites, search_view, process_checkout, admin_orders_view, order_history, change_order_status, admin_order_edit, admin_order_delete, brand_products, country_products
urlpatterns = [
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('add-to-favorites/<int:product_id>/', add_to_favorites, name='add_to_favorites'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('all', AllProductsList, name='all'),
    path('search/', search_view, name='search'),
    path('checkout/', checkout, name='checkout'),
    path('cart/', cart_view, name='cart_view'),  # Make sure this is correct
    path('checkout/process/', process_checkout, name='process_checkout'),
    path('admin/orders/', admin_orders_view, name='admin_orders'),
    path('order-history/', order_history, name='order_history'),
    path('admin/order/<int:order_id>/change_status/', change_order_status, name='admin_order_change_status'),
    path('admin/orders/edit/<int:id>/', admin_order_edit, name='admin_order_edit'),
    path('admin/orders/delete/<int:order_id>/', admin_order_delete, name='admin_order_delete'),
    path('favorites/', favorites_view, name='favorites'),
    path('remove-from-cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),  # Make sure this is correct
    path('remove-from-favorites/<int:product_id>/', remove_from_favorites, name='remove_from_favorites'),
    path('brands/<int:company_id>/', brand_products, name='brand_detail'),
    path('country/<str:country_name>/', country_products, name='country_products'),
]