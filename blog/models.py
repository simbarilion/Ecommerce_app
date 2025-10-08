from django.db import models


class Blogpost(models.Model):
    title = models.CharField(max_length=100,
                             verbose_name="Заголовок")
    author = models.CharField(max_length=100,
                              verbose_name="Автор")
    content = models.TextField(verbose_name="Контент",)
    preview = models.ImageField(upload_to="blog/images/",
                                null=True,
                                blank=True,
                                verbose_name="Превью")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания")
    is_published = models.BooleanField(default=False,
                                       verbose_name="Опубликовано")
    number_of_views = models.IntegerField(default=0,
                                          verbose_name="Количество просмотров")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "блоговый пост"
        verbose_name_plural = "блоговые посты"
        ordering = ["created_at",]
