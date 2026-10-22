from decimal import Decimal

from menu.models import Product

CART_SESSION_KEY = "cafe_cart"
DELIVERY_FEE = Decimal("15.00")
FREE_DELIVERY_FROM = Decimal("150.00")


def get_cart(request):
    stored = request.session.get(CART_SESSION_KEY, {})
    if not isinstance(stored, dict):
        stored = {}
    try:
        product_ids = [int(key) for key in stored.keys() if str(key).isdigit()]
    except (TypeError, ValueError):
        product_ids = []
    products = Product.objects.filter(pk__in=product_ids).select_related("category")
    items, subtotal, count = [], Decimal("0.00"), 0
    for product in products:
        try:
            quantity = max(0, min(99, int(stored.get(str(product.pk), 0))))
        except (TypeError, ValueError):
            quantity = 0
        if quantity == 0:
            continue
        line_total = product.price * quantity
        items.append({"product": product, "quantity": quantity, "line_total": line_total})
        subtotal += line_total
        count += quantity
    fee = Decimal("0.00") if subtotal >= FREE_DELIVERY_FROM else DELIVERY_FEE
    return {"items": items, "subtotal": subtotal, "delivery_fee": fee, "total": subtotal + fee, "count": count}
