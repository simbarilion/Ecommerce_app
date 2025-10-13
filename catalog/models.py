from django.db import models
from django.utils.text import slugify


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
    slug = models.SlugField(unique=True, blank=True)
    brief_description = models.TextField(null=True,
                                         blank=True,
                                         verbose_name="Краткое описание товара")
    description = models.TextField(null=True,
                                   blank=True,
                                   verbose_name="Полное описание товара")
    image = models.ImageField(upload_to="products/images/",
                              null=True,
                              blank=True,
                              verbose_name="Изображение")
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

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name}: {self.price}"


    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"
        ordering = ["name",]


class Contacts(models.Model):
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
    name = models.CharField(max_length=150, verbose_name="Имя пользователя")
    phone = models.CharField(max_length=20, verbose_name="Номер телефона пользователя")
    message = models.TextField(verbose_name="Сообщение пользователя")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.name} {self.phone} {self.message}"

    class Meta:
        verbose_name = "обратная связь"
        verbose_name_plural = "обратная связь"
        ordering = ["name", "phone", "created_at",]
