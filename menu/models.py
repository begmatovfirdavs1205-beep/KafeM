from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField("Название", max_length=100, unique=True)
    slug = models.SlugField("Ссылка", max_length=120, unique=True, blank=True, allow_unicode=True)
    description = models.CharField("Описание", max_length=240, blank=True)
    image = models.ImageField("Фотография", upload_to="categories/", blank=True)
    image_url = models.URLField("Ссылка на фотографию", blank=True)
    sort_order = models.PositiveIntegerField("Порядок сортировки", default=0)
    is_active = models.BooleanField("Показывать на сайте", default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "категория"
        verbose_name_plural = "Категории блюд"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", verbose_name="Категория")
    name = models.CharField("Название", max_length=140)
    slug = models.SlugField("Ссылка", max_length=160, unique=True, blank=True, allow_unicode=True)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена, сомони", max_digits=9, decimal_places=2, validators=[MinValueValidator(0.01)])
    image = models.ImageField("Фотография", upload_to="products/", blank=True)
    image_url = models.URLField("Ссылка на фотографию", blank=True)
    is_available = models.BooleanField("В наличии", default=True)
    is_featured = models.BooleanField("Популярное блюдо", default=False)
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        ordering = ["category__sort_order", "name"]
        verbose_name = "блюдо"
        verbose_name_plural = "Блюда"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
