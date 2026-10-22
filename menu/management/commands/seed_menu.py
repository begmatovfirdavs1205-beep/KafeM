from django.core.management.base import BaseCommand
from django.utils.text import slugify

from menu.models import Category, Product


MENU = [
    ("Бургеры", "photo-1568901346375-23c9450c58cd", [("Классический бургер", "Сочная говяжья котлета, сыр, свежие овощи и фирменный соус.", "49.00"), ("Бургер с курицей", "Хрустящая курица, салат, томаты и сливочный соус.", "45.00")]),
    ("Пицца", "photo-1579751626657-72bc17010498", [("Маргарита", "Томатный соус, моцарелла и ароматный базилик.", "54.00"), ("Пицца с курицей", "Курица, грибы, моцарелла и нежный соус.", "68.00")]),
    ("Шашлык", "photo-1544025162-d76694265947", [("Шашлык из курицы", "Нежное куриное филе с пряными специями и луком.", "62.00"), ("Люля-кебаб", "Рубленое мясо на углях с лепёшкой и зеленью.", "72.00")]),
    ("Горячие блюда", "photo-1547592180-85f173990554", [("Плов по-домашнему", "Рассыпчатый рис, нежная говядина, морковь и зира.", "48.00"), ("Курица с рисом", "Куриное филе с рисом и сезонными овощами.", "43.00")]),
    ("Салаты", "photo-1512621776951-a57141f2eefd", [("Греческий салат", "Свежие овощи, сыр, маслины и оливковая заправка.", "35.00"), ("Салат с курицей", "Куриное филе, хрустящие листья салата и соус.", "39.00")]),
    ("Закуски", "photo-1541529086526-db283c563270", [("Картофель фри", "Золотистый картофель с щепоткой морской соли.", "18.00"), ("Куриные наггетсы", "Нежное куриное филе в хрустящей панировке.", "25.00")]),
    ("Десерты", "photo-1563805042-7684c019e1cb", [("Чизкейк", "Нежный сливочный чизкейк на песочной основе.", "24.00"), ("Шоколадный брауни", "Тёплый шоколадный десерт с насыщенным вкусом какао.", "21.00")]),
    ("Кофе и чай", "photo-1501339847302-ac426a4a7cbb", [("Капучино", "Эспрессо с бархатной молочной пеной.", "16.00"), ("Чай с чабрецом", "Ароматный чёрный чай с горным чабрецом.", "12.00")]),
    ("Напитки", "photo-1513558161293-cacf1e6e2c82", [("Домашний лимонад", "Освежающий лимонад с лимоном и мятой.", "14.00"), ("Компот из сухофруктов", "Домашний напиток с лёгкой фруктовой сладостью.", "10.00")]),
    ("Комбо", "photo-1555939594-58d7cb561ad1", [("Комбо обед", "Горячее блюдо, салат и напиток по специальной цене.", "89.00"), ("Комбо для двоих", "Две порции горячего, закуска и два напитка.", "139.00")]),
]


def image_url(photo_id):
    return f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=900&q=82"


class Command(BaseCommand):
    help = "Добавляет демонстрационные категории и блюда без создания дублей."

    def handle(self, *args, **options):
        products_created = 0
        for sort_order, (category_name, photo_id, products) in enumerate(MENU, start=1):
            category_slug = slugify(category_name, allow_unicode=True)
            category, _ = Category.objects.update_or_create(
                slug=category_slug,
                defaults={"name": category_name, "image_url": image_url(photo_id), "sort_order": sort_order, "is_active": True},
            )
            for index, (name, description, price) in enumerate(products):
                Product.objects.update_or_create(
                    slug=slugify(name, allow_unicode=True),
                    defaults={
                        "category": category, "name": name, "description": description, "price": price,
                        "image_url": image_url(photo_id), "is_available": True, "is_featured": index == 0 and sort_order in (1, 2, 3, 5),
                    },
                )
                products_created += 1
        self.stdout.write(self.style.SUCCESS(f"Готово: {len(MENU)} категорий и {products_created} демонстрационных блюд."))
