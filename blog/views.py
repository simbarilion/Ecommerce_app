from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .forms import BlogpostForm
from .models import Blogpost


class BlogpostListView(ListView):
    """Представление для отображения статей Блога"""
    model = Blogpost
    context_object_name = "blogposts"
    limit = None

    def get_queryset(self):
        if self.template_name == "blog/blogpost_list.html":  # шаблон редактора
            queryset = Blogpost.objects.filter(status__in=["published", "moderation"]).order_by("-created_at")
        else:
            queryset = Blogpost.objects.filter(status="published").order_by("-created_at")
        return queryset[:self.limit] if self.limit else queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_posts"] = Blogpost.objects.filter(status="published").count()
        context["total_authors"] = Blogpost.objects.filter(status="published").values("author").distinct().count()
        return context


class BlogpostDetailView(DetailView):
    """Представление для отображения статьи Блога"""
    model = Blogpost
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author_posts_count"] = Blogpost.objects.filter(author=self.object.author).count()
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.status == "published":
            obj.number_of_views += 1
            obj.save()
        return obj


class BlogpostCreateView(CreateView):
    """Представление для создания статьи Блога"""
    model = Blogpost
    template_name = "blog/blogpost_form.html"
    form_class = BlogpostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = "moderation"
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("blog:blogpost_list")


class BlogpostUpdateView(UpdateView):
    """Представление для редактирования статьи Блога"""
    model = Blogpost
    template_name = "blog/blogpost_form.html"
    form_class = BlogpostForm

    def get_success_url(self):
        return reverse_lazy("blog:blogpost_list_detail", kwargs={"pk": self.object.pk})

    # def test_func(self):
    #     """Проверка пользователя на авторство"""
    #     blogpost = self.get_object()
    #     return self.request.user == blogpost.author
    #
    # def handle_no_permission(self):
    #     """Вызывается, если пользователь не является автором статьи"""
    #     messages.error(self.request, "Вы не можете редартировать чужую статью")
    #     return HttpResponseRedirect(self.success_url)
    #
    # def form_valid(self, form):
    #     form.instance.author = self.request.user
    #     form.instance.status = "moderation"
    #     messages.success(self.request, f"Статья «{form.instance.title}» обновлена и отправлена на модерацию")
    #     return super().form_valid(form)


class BlogpostDeleteView(DeleteView):
    """Представление для удаления статьи Блога"""
    model = Blogpost
    template_name = "blog/blogpost_delete.html"
    success_url = reverse_lazy("blog:blogpost_list")
    context_object_name = "blogpost"

    # def test_func(self):
    #     """Проверка пользователя на авторство"""
    #     blogpost = self.get_object()
    #     return self.request.user == blogpost.author

    # def handle_no_permission(self):
    #     """Вызывается, если пользователь не является автором статьи"""
    #     blogpost = self.get_object()
    #     messages.error(self.request, "Вы не можете удалить чужую статью")
    #     self.object = blogpost
    #     context = self.get_context_data()
    #     return self.render_to_response(context)
    #
    # def delete(self, request, *args, **kwargs):
    #     """Архивирует статью"""
    #     blogpost = self.get_object()
    #     blogpost.status = "archived"
    #     blogpost.save()
    #     messages.success(request, f"Статья «{blogpost.title}» перемещена в архив")
    #     return HttpResponseRedirect(self.success_url)
