from decimal import Decimal
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from menu.models import Category, Product
from orders.models import Order


class CartAndCheckoutTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Бургеры", slug="burgery")
        self.product = Product.objects.create(category=self.category, name="Бургер", slug="burger", price=Decimal("49.00"))

    def test_public_pages_render_russian_category_and_product_slugs(self):
        self.category.slug = "\u0431\u0443\u0440\u0433\u0435\u0440\u044b"
        self.category.save()
        self.product.slug = "\u0431\u0443\u0440\u0433\u0435\u0440"
        self.product.save()

        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("category", args=[self.category.slug])).status_code, 200)
        self.assertEqual(self.client.get(reverse("product_detail", args=[self.product.slug])).status_code, 200)

    def test_add_update_and_remove_cart_items(self):
        response = self.client.post(reverse("cart_add", args=[self.product.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session["cafe_cart"][str(self.product.pk)], 1)
        self.client.post(reverse("cart_update", args=[self.product.pk]), {"quantity": 3})
        self.assertEqual(self.client.session["cafe_cart"][str(self.product.pk)], 3)
        self.client.post(reverse("cart_update", args=[self.product.pk]), {"action": "remove"})
        self.assertEqual(self.client.session["cafe_cart"], {})

    def test_cannot_add_unavailable_product(self):
        self.product.is_available = False
        self.product.save()
        response = self.client.post(reverse("cart_add", args=[self.product.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.session.get("cafe_cart", {}), {})

    def test_checkout_saves_price_snapshot_and_delivery_fee(self):
        self.client.post(reverse("cart_add", args=[self.product.pk]))
        self.client.get(reverse("checkout"))
        checkout_key = self.client.session["checkout_key"]
        response = self.client.post(reverse("checkout"), {
            "checkout_key": checkout_key,
            "customer_name": "Амина",
            "phone": "+992 900 12 34 56",
            "fulfillment": Order.Fulfillment.DELIVERY,
            "address": "Душанбе, Рудаки 10",
            "comment": "Без лука",
        })
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get()
        item = order.items.get()
        self.assertEqual(order.subtotal, Decimal("49.00"))
        self.assertEqual(order.delivery_fee, Decimal("15.00"))
        self.assertEqual(order.total, Decimal("64.00"))
        self.assertEqual(item.unit_price, Decimal("49.00"))
        self.assertEqual(order.status, Order.Status.NEW)
        self.assertEqual(self.client.session["cafe_cart"], {})
        duplicate_response = self.client.post(reverse("checkout"), {
            "checkout_key": checkout_key,
            "customer_name": "Амина",
            "phone": "+992 900 12 34 56",
            "fulfillment": Order.Fulfillment.DELIVERY,
            "address": "Душанбе, Рудаки 10",
        })
        self.assertRedirects(duplicate_response, reverse("order_success", args=[order.public_token]), fetch_redirect_response=False)
        self.assertEqual(Order.objects.count(), 1)

    def test_checkout_uses_current_server_price(self):
        self.client.post(reverse("cart_add", args=[self.product.pk]))
        self.client.get(reverse("checkout"))
        key = self.client.session["checkout_key"]
        self.product.price = Decimal("55.00")
        self.product.save()
        self.client.post(reverse("checkout"), {"checkout_key": key, "customer_name": "Амина", "phone": "900123456", "fulfillment": "pickup"})
        self.assertEqual(Order.objects.get().total, Decimal("55.00"))

    def test_status_lookup_uses_unpredictable_token(self):
        self.client.post(reverse("cart_add", args=[self.product.pk]))
        self.client.get(reverse("checkout"))
        self.client.post(reverse("checkout"), {"checkout_key": self.client.session["checkout_key"], "customer_name": "Амина", "phone": "900123456", "fulfillment": "pickup"})
        order = Order.objects.get()
        response = self.client.get(reverse("order_status", args=[order.public_token]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, order.order_number)

    def test_admin_can_print_and_export_an_order(self):
        order = Order.objects.create(
            checkout_key=uuid.uuid4(), customer_name="Амина", phone="900123456",
            address="Душанбе", subtotal=Decimal("49.00"), delivery_fee=Decimal("15.00"), total=Decimal("64.00"),
        )
        staff = get_user_model().objects.create_superuser(username="ordersadmin", email="orders@example.com", password="secure-test-password")
        self.client.force_login(staff)
        print_response = self.client.get(reverse("admin:orders_order_print", args=[order.pk]))
        self.assertEqual(print_response.status_code, 200)
        self.assertContains(print_response, order.order_number)
        export_response = self.client.post(reverse("admin:orders_order_changelist"), {
            "action": "export_orders_csv", "_selected_action": [str(order.pk)],
        })
        self.assertEqual(export_response.status_code, 200)
        self.assertIn(order.order_number.encode(), export_response.content)
