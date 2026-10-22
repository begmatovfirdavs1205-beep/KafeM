import uuid

from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        CONFIRMED = "confirmed", "Подтверждён"
        COOKING = "cooking", "Готовится"
        READY = "ready", "Готов к выдаче"
        COURIER = "courier", "Передан курьеру"
        COMPLETED = "completed", "Выполнен"
        CANCELLED = "cancelled", "Отменён"

    class Fulfillment(models.TextChoices):
        DELIVERY = "delivery", "Доставка"
        PICKUP = "pickup", "Самовывоз"

    order_number = models.CharField("Номер заказа", max_length=24, unique=True, editable=False)
    public_token = models.UUIDField("Код проверки", default=uuid.uuid4, unique=True, editable=False)
    checkout_key = models.UUIDField("Ключ оформления", unique=True, editable=False)
    customer_name = models.CharField("Имя клиента", max_length=120)
    phone = models.CharField("Телефон", max_length=30)
    address = models.CharField("Адрес доставки", max_length=250, blank=True)
    comment = models.TextField("Комментарий", blank=True)
    fulfillment = models.CharField("Способ получения", max_length=12, choices=Fulfillment.choices, default=Fulfillment.DELIVERY)
    payment_method = models.CharField("Оплата", max_length=40, default="Наличными при получении")
    subtotal = models.DecimalField("Стоимость блюд, сомони", max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField("Доставка, сомони", max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField("Итого, сомони", max_digits=10, decimal_places=2)
    status = models.CharField("Статус", max_length=16, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField("Дата и время", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"MK-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey("menu.Product", on_delete=models.SET_NULL, null=True, blank=True, related_name="order_items", verbose_name="Блюдо")
    product_name = models.CharField("Блюдо", max_length=140)
    unit_price = models.DecimalField("Цена на момент заказа", max_digits=9, decimal_places=2)
    quantity = models.PositiveIntegerField("Количество")
    line_total = models.DecimalField("Сумма", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "позиция заказа"
        verbose_name_plural = "Состав заказа"

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"
