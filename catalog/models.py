from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100,
                            unique=True,
                            verbose_name="Наименование категории")
    description = models.TextField(null=True,
                                   blank=True,
                                   verbose_name="Описание категории")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"
        ordering = ["name",]


def get_default_category():
    category, created = Category.objects.get_or_create(
        name="Без категории",
        defaults={"description": "Категория по умолчанию"}
    )
    return category.id


class Product(models.Model):
    name = models.CharField(max_length=150,
                            unique=True,
                            verbose_name="Наименование товара")
    description = models.TextField(null=True,
                                   blank=True,
                                   verbose_name="Описание товара")
    image = models.FilePathField(path="static/images")
    category = models.ForeignKey(to=Category,
                                 on_delete=models.CASCADE,
                                 related_name="products",
                                 default=get_default_category)
    price = models.FloatField(null=False,
                              verbose_name="Цена товара",
                              help_text="Введите число с плавающей точкой")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name="Дата последнего изменения")

    def __str__(self):
        return f"{self.name}: {self.price}"

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"
        ordering = ["name",]
