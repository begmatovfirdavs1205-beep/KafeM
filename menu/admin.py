from django.contrib import admin

from core.admin_site import cafe_admin_site
from menu.models import Category, Product


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_available", "is_featured")
    list_filter = ("category", "is_available", "is_featured")
    list_editable = ("price", "is_available", "is_featured")
    search_fields = ("name", "description")
    list_select_related = ("category",)
    autocomplete_fields = ("category",)


cafe_admin_site.register(Category, CategoryAdmin)
cafe_admin_site.register(Product, ProductAdmin)
