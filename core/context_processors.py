from orders.cart import get_cart


def cart_summary(request):
    cart = get_cart(request)
    return {"cart_count": cart["count"], "cart_subtotal": cart["subtotal"]}
