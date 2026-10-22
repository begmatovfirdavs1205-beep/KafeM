from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from menu.models import Category, Product


class HomePageTests(TestCase):
    def test_homepage_loads_in_russian(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Вкусные блюда")
        self.assertContains(response, "доставкой")

    def test_admin_requires_login(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)

    def test_admin_dashboard_loads_for_staff(self):
        user = get_user_model().objects.create_superuser(username="cafeadmin", email="admin@example.com", password="secure-test-password")
        self.client.force_login(user)
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Заказов сегодня")
        self.assertContains(response, "Блюда")
        self.assertContains(response, "adminlte.min.css")
        self.assertContains(response, "css/jazzmin.css")

    def test_combo_offer_uses_current_menu_price(self):
        category = Category.objects.create(name="Комбо", slug="kombo")
        Product.objects.create(category=category, name="Обеденное комбо", slug="obed-kombo", price=Decimal("89.00"))
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Обеденное комбо")
        self.assertContains(response, "89,00 сомони")
