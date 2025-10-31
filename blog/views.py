from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .forms import BlogpostForm, BlogpostContentManagerForm
from .models import Blogpost
from .services.blogpost_service import is_content_manager, get_visible_blogposts_for_user, can_user_view_blogpost, \
    check_user_can_create_blogpost, update_blogpost_status_on_edit, check_user_can_edit_blogpost, \
    check_user_can_delete_blogpost, archive_blogpost, search_blogposts


class BlogpostListView(ListView):
    """Представление для отображения статей Блога"""
    model = Blogpost
    context_object_name = "blogposts"
    paginate_by = None
    template_name = None
    limit = None


    def get_context_data(self, **kwargs):
        """Добавляет количество публикаций и авторов в контекст, создает контекст для поискового запроса"""
        context = super().get_context_data(**kwargs)
        context["total_posts"] = Blogpost.objects.filter(status="published").count()
        context["total_authors"] = Blogpost.objects.filter(status="published").values("author").distinct().count()
        context["search_type"] = "blog"
        return context


    def get_queryset(self):
        """Возвращает статьи блога в зависимости от статуса публикации и прав пользователя"""
        return get_visible_blogposts_for_user(
            user=self.request.user,
            template_name=self.template_name,
            limit=self.limit
        )


@method_decorator(cache_page(60 * 15), name="dispatch")
class BlogpostDetailView(DetailView):
    """Представление для отображения статьи Блога"""
    model = Blogpost
    context_object_name = "post"


    def get_object(self, queryset=None):
        """Показывает статью, если она опубликован или если пользователь имеет права просмотр неопубликованных статей"""
        post = super().get_object(queryset)
        can_user_view_blogpost(self.request.user, post)
        return post


    def get_context_data(self, **kwargs):
        """Добавляет количество публикаций автора в контекст"""
        context = super().get_context_data(**kwargs)
        context["author_posts_count"] = Blogpost.objects.filter(author=self.object.author).count()
        return context


class BlogpostCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания статьи Блога"""
    model = Blogpost
    template_name = "blog/blogpost_form.html"
    form_class = BlogpostForm


    def get_context_data(self, **kwargs):
        """Определяет контекст с объектом статьи"""
        context = super().get_context_data(**kwargs)
        context["obj"] = None
        return context


    def form_valid(self, form):
        """Присваивает текущего авторизованного пользователя как автора статьи, устанавливает статус 'moderation'"""
        form.instance.author = self.request.user
        form.instance.status = "moderation"
        return super().form_valid(form)


    def dispatch(self, request, *args, **kwargs):
        """Запрещает контент-менеджерам создавать статьи"""
        check_user_can_create_blogpost(request.user)
        return super().dispatch(request, *args, **kwargs)


    def get_success_url(self):
        """При успешном создании статьи возвращает на страницу редактора статей"""
        return reverse_lazy("blog:blogpost_list")


class BlogpostUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования статьи Блога"""
    model = Blogpost
    template_name = "blog/blogpost_form.html"
    form_class = BlogpostForm


    def get_context_data(self, **kwargs):
        """Возвращает контекст с объектом статьи"""
        context = super().get_context_data(**kwargs)
        context["obj"] = self.object
        return context


    def form_valid(self, form):
        """Устанавливает при редактировании статус статьи 'moderation'"""
        post = self.get_object()
        update_blogpost_status_on_edit(post, self.request.user, form)
        return super().form_valid(form)


    def get_object(self, queryset=None):
        """Возвращает объект только если пользователь — автор статьи"""
        if not hasattr(self, "_cached_object"):
            self._cached_object = super().get_object(queryset)
            check_user_can_edit_blogpost(self.request.user, self._cached_object)
        return self._cached_object


    def get_form_class(self):
        """Выбирает форму в зависимости от статуса пользователя"""
        user = self.request.user
        obj = self.get_object()

        if is_content_manager(user) and obj.author != user:
            return BlogpostContentManagerForm
        return BlogpostForm


    def handle_no_permission(self):
        """Если пользователь не авторизован, перенаправляет на страницу авторизации"""
        if not self.request.user.is_authenticated:
            return redirect("users:login")
        raise PermissionDenied("У вас нет прав для редактирования товара")


    def get_success_url(self):
        """При успешном редактировании статьи возвращает на страницу просмотра статьи"""
        return reverse_lazy("blog:blogpost_list_detail", kwargs={"pk": self.object.pk})


class BlogpostDeleteView(LoginRequiredMixin, DeleteView):
    """Представление для удаления статьи Блога"""
    model = Blogpost
    template_name = "blog/blogpost_delete.html"
    success_url = reverse_lazy("blog:blogpost_list")
    context_object_name = "blogpost"

    def get_object(self, queryset=None):
        """Возвращает объект только если пользователь — автор статьи или имеет права контент-менеджера"""
        post = super().get_object(queryset)
        check_user_can_delete_blogpost(self.request.user, post)
        return post


    def handle_no_permission(self):
        """Если пользователь не авторизован, перенаправляет на страницу авторизации"""
        if not self.request.user.is_authenticated:
            return redirect("users:login")
        raise PermissionDenied("У вас нет прав для удаления статьи")


    def post(self, request, *args, **kwargs):
        """Помечает статью как 'archived' вместо физического удаления"""
        post = self.get_object()
        archive_blogpost(post, request.user)
        return HttpResponseRedirect(self.success_url)


def blogpost_search_view(request):
    """Осуществляет поисковый запрос статей блога"""
    query = request.GET.get("q", "").strip()
    blogposts = search_blogposts(query)

    paginator = Paginator(blogposts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "search_type": "blog",
        "query": query,
        "page_obj": page_obj,
    }
    return render(request, "blog/blogpost_search.html", context)
