from datetime import timedelta
from decimal import Decimal

from django.contrib.admin import AdminSite
from django.db.models import Sum
from django.utils import timezone


class CafeAdminSite(AdminSite):
    site_header = "Моё Кафе — Администрирование"
    site_title = "Моё Кафе"
    index_title = "Панель управления кафе"

    def index(self, request, extra_context=None):
        from orders.models import Order, OrderItem

        today = timezone.localdate()
        month_start = today.replace(day=1)
        today_orders = Order.objects.filter(created_at__date=today)
        month_orders = Order.objects.filter(created_at__date__gte=month_start)
        completed = Order.Status.COMPLETED
        stats = {
            "orders_today": today_orders.count(),
            "new_orders": Order.objects.filter(status=Order.Status.NEW).count(),
            "completed_orders": Order.objects.filter(status=completed).count(),
            "revenue_today": today_orders.filter(status=completed).aggregate(total=Sum("total"))["total"] or Decimal("0.00"),
            "revenue_month": month_orders.filter(status=completed).aggregate(total=Sum("total"))["total"] or Decimal("0.00"),
            "popular_dishes": list(
                OrderItem.objects.filter(order__status=completed, order__created_at__date__gte=today - timedelta(days=30))
                .values("product_name").annotate(sold=Sum("quantity")).order_by("-sold")[:5]
            ),
        }
        context = {"cafe_stats": stats}
        if extra_context:
            context.update(extra_context)
        return super().index(request, extra_context=context)


cafe_admin_site = CafeAdminSite(name="admin")
