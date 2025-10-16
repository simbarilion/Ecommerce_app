from django.db import models

from django.contrib.auth.models import User


class Blogpost(models.Model):
    STATUS_CHOICES = [
        ("moderation", "На модерации"),
        ("published", "Опубликовано"),
        ("archived", "В архиве"),
    ]

    title = models.CharField(max_length=150,
                             verbose_name="Заголовок статьи")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts",
                               verbose_name="Автор")
    content = models.TextField(verbose_name="Содержание статьи",)
    preview = models.ImageField(upload_to="blog/images/",
                                null=True,
                                blank=True,
                                verbose_name="Изображение",
                                default="images/default.png")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name="Дата последнего изменения")
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES,
                              default="moderation",
                              verbose_name="Статус")
    number_of_views = models.PositiveIntegerField(default=0,
                                                  verbose_name="Количество просмотров")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "блоговый пост"
        verbose_name_plural = "блоговые посты"
        ordering = ["created_at",]
