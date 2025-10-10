from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=100,
                                  verbose_name="Имя")
    last_name = models.CharField(max_length=100,
                                 null=True,
                                 blank=True,
                                 verbose_name="Фамилия")
    email = models.EmailField(max_length=254,
                              verbose_name="Адрес электронной почты")

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.last_name else self.first_name

    class Meta:
        verbose_name = "автор"
        verbose_name_plural = "авторы"
        ordering = ["last_name", "first_name",]


class Blogpost(models.Model):
    title = models.CharField(max_length=100,
                             verbose_name="Заголовок")
    author = models.ForeignKey(Author,
                               on_delete=models.CASCADE,
                               related_name="posts",
                               verbose_name="Автор")
    content = models.TextField(verbose_name="Контент",)
    preview = models.ImageField(upload_to="blog/images/",
                                null=True,
                                blank=True,
                                verbose_name="Превью")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name="Дата последнего изменения")
    is_published = models.BooleanField(default=True,
                                       verbose_name="Опубликовано")
    number_of_views = models.PositiveIntegerField(default=0,
                                                  verbose_name="Количество просмотров")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "блоговый пост"
        verbose_name_plural = "блоговые посты"
        ordering = ["created_at",]
