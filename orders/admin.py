import csv

from django.contrib import admin
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html

from core.admin_site import cafe_admin_site
from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "unit_price", "quantity", "line_total")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.action(description="Экспортировать выбранные заказы в CSV")
def export_orders_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="orders.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Номер", "Дата", "Клиент", "Телефон", "Адрес", "Блюда", "Сумма, сомони", "Получение", "Комментарий", "Статус"])
    for order in queryset.prefetch_related("items"):
        items = ", ".join(f"{i.product_name} × {i.quantity}" for i in order.items.all())
        writer.writerow([order.order_number, order.created_at.strftime("%d.%m.%Y %H:%M"), order.customer_name, order.phone, order.address, items, order.total, order.get_fulfillment_display(), order.comment, order.get_status_display()])
    return response


class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "created_at", "customer_name", "phone", "total", "fulfillment", "status", "print_link")
    list_filter = ("status", "fulfillment", ("created_at", admin.DateFieldListFilter))
    search_fields = ("order_number", "phone", "customer_name")
    date_hierarchy = "created_at"
    list_per_page = 30
    list_select_related = ()
    readonly_fields = ("order_number", "public_token", "checkout_key", "customer_name", "phone", "address", "comment", "fulfillment", "payment_method", "subtotal", "delivery_fee", "total", "created_at")
    inlines = (OrderItemInline,)
    actions = (export_orders_csv,)
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    @admin.display(description="Печать")
    def print_link(self, obj):
        return format_html('<a href="{}" target="_blank">Печать</a>', reverse("admin:orders_order_print", args=[obj.pk]))

    def get_urls(self):
        return [path("<path:object_id>/print/", self.admin_site.admin_view(self.print_order), name="orders_order_print")] + super().get_urls()

    def print_order(self, request, object_id):
        order = self.get_object(request, object_id)
        if order is None:
            from django.http import Http404
            raise Http404
        return TemplateResponse(request, "admin/orders/order/print.html", {"order": order, "opts": self.model._meta})


cafe_admin_site.register(Order, OrderAdmin)
