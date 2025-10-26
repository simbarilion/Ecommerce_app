import re

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .forms import BlogpostForm, BlogpostContentManagerForm
from .models import Blogpost
from .utils import is_content_manager


class BlogpostListView(ListView):
    """Представление для отображения статей Блога"""
    model = Blogpost
    context_object_name = "blogposts"
    paginate_by = None
    template_name = None
    limit = None


    def get_queryset(self):
        """Возвращает статьи блога в зависимости от статуса публикации и прав пользователя"""
        user = self.request.user
        queryset = Blogpost.objects.all().order_by("-created_at")

        if self.template_name == "blog/main.html":
            queryset = queryset.filter(status="published")
        else:
            if user.is_authenticated:
                if is_content_manager(user):
                    queryset = queryset.filter(status__in=["published", "moderation", "archived"])
                else:
                    queryset = queryset.filter(
                        Q(status="published") |
                        Q(status="moderation", author=user)
                    )
            else:
                queryset = queryset.filter(status="published")

        return queryset[:self.limit] if self.limit else queryset


    def get_context_data(self, **kwargs):
        """Добавляет количество публикаций и авторов в контекст, создает контекст для поискового запроса"""
        context = super().get_context_data(**kwargs)
        context["total_posts"] = Blogpost.objects.filter(status="published").count()
        context["total_authors"] = Blogpost.objects.filter(status="published").values("author").distinct().count()
        context["search_type"] = "blog"
        return context


class BlogpostDetailView(DetailView):
    """Представление для отображения статьи Блога"""
    model = Blogpost
    context_object_name = "post"

    def get_object(self, queryset=None):
        """Показывает статью, если она опубликован или если пользователь имеет права просмотр неопубликованных статей"""
        obj = super().get_object(queryset)
        user = self.request.user

        if user.is_authenticated:
            if is_content_manager(user):
                if obj.status not in ["published", "moderation", "archived"]:
                    raise Http404("Статья недоступна")
            else:
                if obj.status == "moderation" and obj.author != user:
                    raise Http404("Статья недоступна")
                if obj.status == "archived" or obj.status not in ["published", "moderation"]:
                    raise Http404("Статья недоступна")
                if obj.status not in ["published", "moderation", "archived"]:
                    raise Http404("Статья недоступна")
        else:
            if obj.status != "published":
                raise Http404("Статья недоступна")

        if obj.status == "published":
            obj.number_of_views += 1
            obj.save()

        return obj

    def get_context_data(self, **kwargs):
        """Добавляет количество публикаций автора в контекст"""
        context = super().get_context_data(**kwargs)
        context["author_posts_count"] = Blogpost.objects.filter(author=self.object.author).count()
        return context


class BlogpostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Представление для создания статьи Блога"""
    model = Blogpost
    template_name = "blog/blogpost_form.html"
    form_class = BlogpostForm
    permission_required = "blog.add_blogpost"


    def form_valid(self, form):
        """Присваивает текущего авторизованного пользователя как автора статьи, устанавливает статус 'moderation'"""
        form.instance.author = self.request.user
        form.instance.status = "moderation"
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        """Запрещает контент-менеджерам создавать статьи"""
        user = request.user
        if is_content_manager(user):
            raise PermissionDenied("Контент-менеджерам запрещено создавать товары")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """При успешном создании статьи возвращает на страницу редактора статей"""
        return reverse_lazy("blog:blogpost_list")


class BlogpostUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования статьи Блога"""
    model = Blogpost
    template_name = "blog/blogpost_form.html"
    form_class = BlogpostForm

    def form_valid(self, form):
        """Устанавливает при редактировании статус статьи 'moderation'"""
        user = self.request.user
        obj = self.get_object()
        if obj.author == user:
            form.instance.status = "moderation"
        return super().form_valid(form)

    def get_object(self, queryset=None):
        """Возвращает объект только если пользователь — автор статьи"""
        if not hasattr(self, "_cached_object"):
            self._cached_object = super().get_object(queryset)
            user = self.request.user

            if self._cached_object.author != user and not is_content_manager(user):
                raise PermissionDenied("Вы не можете редактировать чужую статью")
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
        obj = super().get_object(queryset)
        user = self.request.user

        if obj.author != user and not is_content_manager(user):
            raise PermissionDenied("Вы не можете удалить чужую статью")
        return obj

    def handle_no_permission(self):
        """Если пользователь не авторизован, перенаправляет на страницу авторизации"""
        if not self.request.user.is_authenticated:
            return redirect("users:login")
        raise PermissionDenied("У вас нет прав для удаления статьи")

    def post(self, request, *args, **kwargs):
        """Помечает статью как 'archived' вместо физического удаления"""
        obj = self.get_object()
        obj.status = "archived"
        obj.save()
        return HttpResponseRedirect(self.success_url)


def blogpost_search_view(request):
    """Осуществляет поисковый запрос статей блога"""
    query = request.GET.get("q", "").strip()
    blogposts = Blogpost.objects.none()

    if query:
        keywords = re.findall(r'\w+', query)

        q_objects = Q()
        for word in keywords:
            q_objects |= (Q(title__icontains=word) | Q(content__icontains=word))

        blogposts = Blogpost.objects.filter(q_objects, status="published").distinct()

    paginator = Paginator(blogposts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "search_type": "blog",
        "query": query,
        "page_obj": page_obj,
    }
    return render(request, "blog/blogpost_search.html", context)
