from django.shortcuts import get_object_or_404, render

from menu.models import Category, Product


def product_list(request, slug=None):
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_available=True, category__is_active=True).select_related("category")
    selected_category = None
    if slug:
        selected_category = get_object_or_404(categories, slug=slug)
        products = products.filter(category=selected_category)
    elif request.GET.get("category"):
        selected_category = get_object_or_404(categories, slug=request.GET["category"])
        products = products.filter(category=selected_category)
    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(name__icontains=query)
    return render(request, "menu/list.html", {"categories": categories, "products": products, "selected_category": selected_category, "query": query})


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_available=True, category__is_active=True)
    return render(request, "menu/detail.html", {"product": product})
