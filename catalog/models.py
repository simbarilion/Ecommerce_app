from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    """Класс категории товаров"""
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
    """Устанавлмвает категорию по кмолчанию 'Без категории'"""
    category, created = Category.objects.get_or_create(
        name="Без категории",
        defaults={"description": "Категория по умолчанию"}
    )
    return category.id


class Product(models.Model):
    """Класс товаров"""
    name = models.CharField(max_length=150,
                            unique=True,
                            verbose_name="Наименование товара")
    brief_description = models.TextField(max_length=100,
                                         null=True,
                                         blank=True,
                                         verbose_name="Краткое описание товара")
    description = models.TextField(null=True,
                                   blank=True,
                                   verbose_name="Полное описание товара")
    image = models.ImageField(upload_to="products/images/",
                              null=True,
                              blank=True,
                              verbose_name="Изображение",
                              default="products/images/default.png")
    category = models.ForeignKey(to=Category,
                                 on_delete=models.CASCADE,
                                 related_name="products",
                                 default=get_default_category)
    price = models.FloatField(null=False,
                              verbose_name="Цена товара",
                              help_text="Введите цену в формате 00.0")
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


class Contacts(models.Model):
    """Класс контактной информации"""
    country = models.CharField(max_length=20, verbose_name="Страна")
    address = models.CharField(max_length=150, verbose_name="Юридический адрес")
    email = models.EmailField(max_length=50, verbose_name="Адрес электронной почты")

    def __str__(self):
        return f"{self.country} {self.address} {self.email}"

    class Meta:
        verbose_name = "контакты"
        verbose_name_plural = "контакты"
        ordering = ["country", "address",]


class MessageFeedback(models.Model):
    """Класс обратной связи пользователей"""
    name = models.CharField(max_length=150, verbose_name="Имя пользователя")
    email = models.EmailField(verbose_name="E-mail пользователя")
    message = models.TextField(max_length=2000, verbose_name="Сообщение пользователя")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.name} {self.email} {self.message}"

    class Meta:
        verbose_name = "обратная связь"
        verbose_name_plural = "обратная связь"
        ordering = ["name", "email", "created_at",]
