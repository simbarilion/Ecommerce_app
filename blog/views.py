from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Blogpost


class BlogMainView(ListView):
    model = Blogpost
    template_name = "blog/main.html"
    context_object_name = "latest_posts"

    def get_queryset(self):
        return Blogpost.objects.filter(is_published=True).order_by("created_at")[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["total_posts"] = Blogpost.objects.filter(is_published=True).count()
        context["total_authors"] = Blogpost.objects.filter(is_published=True).values("author").distinct().count()

        return context


class BlogpostsView(ListView):
    model = Blogpost
    template_name = "blog/blogposts.html"
    context_object_name = "blogposts"
    paginate_by = 12

    def get_queryset(self):
        return Blogpost.objects.filter(is_published=True).order_by("created_at")


class BlogpostsDetailView(DetailView):
    model = Blogpost
    template_name = "blog/blogposts_detail.html"
    context_object_name = "blogpost"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_published:
            obj.number_of_views += 1
            obj.save()
        return obj


class BlogpostListView(ListView):
    model = Blogpost
    template_name = "blog/blogpost_list.html"
    context_object_name = "post_list"
    paginate_by = 50

    def get_queryset(self):
        return Blogpost.objects.filter(is_published=True).order_by("created_at")


class BlogpostListDetailView(DetailView):
    model = Blogpost
    template_name = "blog/blogpost_list_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author_posts_count"] = Blogpost.objects.filter(author=self.object.author).count()
        return context


class BlogpostCreateView(CreateView):
    model = Blogpost
    fields = ["title", "author", "content", "preview",]
    template_name = "blog/blogpost_form.html"

    def get_success_url(self):
        return reverse_lazy("blog:blogpost_list")


class BlogpostUpdateView(UpdateView):
    model = Blogpost
    fields = ["title", "author", "content", "preview", "is_published",]
    template_name = "blog/blogpost_form.html"

    def get_success_url(self):
        return reverse_lazy("blog:blogpost_list_detail", kwargs={"pk": self.object.pk})


class BlogpostDeleteView(DeleteView):
    model = Blogpost
    template_name = "blog/blogpost_delete.html"
    success_url = reverse_lazy("blog:blogpost_list")
