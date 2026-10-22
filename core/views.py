from django.shortcuts import render

from menu.models import Category, Product


def home(request):
    categories = Category.objects.filter(is_active=True).order_by("sort_order", "name")
    popular = Product.objects.filter(is_available=True, is_featured=True).select_related("category")[:6]
    if not popular:
        popular = Product.objects.filter(is_available=True).select_related("category")[:6]
    special_offer = Product.objects.filter(category__name__iexact="Комбо", is_available=True).order_by("price").first()
    return render(request, "core/home.html", {"categories": categories, "popular_products": popular, "special_offer": special_offer})


def about(request):
    return render(request, "core/info.html", {"title": "О кафе", "eyebrow": "Тёплое место рядом", "heading": "Готовим с душой, подаём с улыбкой", "body": "«Моё Кафе» — уютная городская кухня с любимыми блюдами на каждый день. Мы готовим после заказа, бережно упаковываем и доставляем горячим."})


def delivery(request):
    return render(request, "core/info.html", {"title": "Доставка", "eyebrow": "Быстро и удобно", "heading": "Ваш заказ скоро будет у двери", "body": "Доставляем по городу ежедневно с 10:00 до 23:00. Стоимость доставки — 15 сомони, а при заказе от 150 сомони доставка бесплатная. Также можно забрать заказ самостоятельно."})


def contacts(request):
    return render(request, "core/info.html", {"title": "Контакты", "eyebrow": "Будем рады видеть вас", "heading": "Давайте знакомиться", "body": "Позвоните нам по номеру +992 900 00 00 00 или приходите в гости: Душанбе, проспект Рудаки, 80. Работаем каждый день с 10:00 до 23:00."})
