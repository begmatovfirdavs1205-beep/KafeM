import uuid
from decimal import Decimal

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from menu.models import Product
from orders.cart import CART_SESSION_KEY, DELIVERY_FEE, FREE_DELIVERY_FROM, get_cart
from orders.forms import CheckoutForm
from orders.models import Order, OrderItem
from orders.services import notify_new_order


@require_http_methods(["GET", "POST"])
def cart_detail(request):
    return render(request, "orders/cart.html", {"cart": get_cart(request)})


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_available=True, category__is_active=True)
    cart = request.session.get(CART_SESSION_KEY, {})
    try:
        current = int(cart.get(str(product.pk), 0))
    except (TypeError, ValueError):
        current = 0
    if current >= 99:
        messages.warning(request, "В корзине уже максимальное количество этого блюда.")
    else:
        cart[str(product.pk)] = current + 1
        request.session[CART_SESSION_KEY] = cart
        request.session["checkout_key"] = str(uuid.uuid4())
        messages.success(request, f"«{product.name}» добавлено в корзину.")
    return redirect("cart")


@require_POST
def cart_update(request, product_id):
    cart = request.session.get(CART_SESSION_KEY, {})
    key = str(product_id)
    action = request.POST.get("action")
    if action == "remove":
        cart.pop(key, None)
    else:
        try:
            quantity = int(request.POST.get("quantity", "1"))
        except (TypeError, ValueError):
            quantity = 0
        product = Product.objects.filter(pk=product_id, is_available=True, category__is_active=True).first()
        if not product:
            cart.pop(key, None)
            messages.warning(request, "Блюдо больше недоступно и удалено из корзины.")
        elif quantity <= 0:
            cart.pop(key, None)
        else:
            cart[key] = min(quantity, 99)
    request.session[CART_SESSION_KEY] = cart
    if not cart:
        request.session.pop("checkout_key", None)
    return redirect("cart")


@require_http_methods(["GET", "POST"])
def checkout(request):
    cart = get_cart(request)
    if not cart["items"]:
        previous_key = request.session.get("checkout_key")
        if previous_key:
            try:
                existing = Order.objects.filter(checkout_key=uuid.UUID(previous_key)).first()
            except (TypeError, ValueError):
                existing = None
            if existing:
                return redirect("order_success", token=existing.public_token)
        messages.info(request, "Добавьте блюда в корзину перед оформлением заказа.")
        return redirect("menu")
    checkout_key = request.session.get("checkout_key")
    if not checkout_key:
        checkout_key = str(uuid.uuid4())
        request.session["checkout_key"] = checkout_key
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        submitted_key = request.POST.get("checkout_key", "")
        if submitted_key != checkout_key:
            form.add_error(None, "Форма устарела. Проверьте данные и отправьте заказ ещё раз.")
        else:
            existing = Order.objects.filter(checkout_key=checkout_key).first()
            if existing:
                return redirect("order_success", token=existing.public_token)
            fresh_products = {p.pk: p for p in Product.objects.filter(pk__in=[item["product"].pk for item in cart["items"]], is_available=True, category__is_active=True).select_related("category")}
            if len(fresh_products) != len(cart["items"]):
                form.add_error(None, "Одно из блюд закончилось. Обновите корзину и попробуйте снова.")
            else:
                subtotal = sum((fresh_products[item["product"].pk].price * item["quantity"] for item in cart["items"]), Decimal("0.00"))
                fulfillment = form.cleaned_data["fulfillment"]
                fee = Decimal("0.00") if fulfillment == Order.Fulfillment.PICKUP or subtotal >= FREE_DELIVERY_FROM else DELIVERY_FEE
                try:
                    with transaction.atomic():
                        order = Order.objects.create(
                            checkout_key=uuid.UUID(checkout_key), customer_name=form.cleaned_data["customer_name"].strip(),
                            phone=form.cleaned_data["phone"], address=form.cleaned_data["address"].strip(),
                            comment=form.cleaned_data["comment"].strip(), fulfillment=fulfillment,
                            subtotal=subtotal, delivery_fee=fee, total=subtotal + fee,
                        )
                        OrderItem.objects.bulk_create([
                            OrderItem(order=order, product=fresh_products[item["product"].pk], product_name=fresh_products[item["product"].pk].name,
                                      unit_price=fresh_products[item["product"].pk].price, quantity=item["quantity"],
                                      line_total=fresh_products[item["product"].pk].price * item["quantity"])
                            for item in cart["items"]
                        ])
                except IntegrityError:
                    order = Order.objects.get(checkout_key=checkout_key)
                else:
                    notify_new_order(order)
                request.session[CART_SESSION_KEY] = {}
                return redirect("order_success", token=order.public_token)
    return render(request, "orders/checkout.html", {"form": form, "cart": cart, "checkout_key": checkout_key})


def order_success(request, token):
    order = get_object_or_404(Order.objects.prefetch_related("items"), public_token=token)
    return render(request, "orders/success.html", {"order": order})


@require_http_methods(["GET", "POST"])
def order_lookup(request):
    order = None
    if request.method == "POST":
        token = request.POST.get("token", "").strip()
        try:
            order = Order.objects.get(public_token=uuid.UUID(token))
        except (ValueError, TypeError, Order.DoesNotExist):
            messages.error(request, "Заказ с таким кодом не найден.")
    return render(request, "orders/lookup.html", {"order": order})


def order_status(request, token):
    order = get_object_or_404(Order.objects.prefetch_related("items"), public_token=token)
    return render(request, "orders/status.html", {"order": order})
