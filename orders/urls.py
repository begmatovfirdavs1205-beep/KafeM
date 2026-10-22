from django.urls import path

from orders import views

urlpatterns = [
    path("cart/", views.cart_detail, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("checkout/", views.checkout, name="checkout"),
    path("success/<uuid:token>/", views.order_success, name="order_success"),
    path("status/", views.order_lookup, name="order_lookup"),
    path("status/<uuid:token>/", views.order_status, name="order_status"),
]
