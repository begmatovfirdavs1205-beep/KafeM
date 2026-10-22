from django.urls import path

from menu import views

urlpatterns = [
    path("", views.product_list, name="menu"),
    # Slugs are generated with allow_unicode=True, so the ASCII-only ``slug``
    # converter rejects Russian category and product names.
    path("category/<str:slug>/", views.product_list, name="category"),
    path("<str:slug>/", views.product_detail, name="product_detail"),
]
