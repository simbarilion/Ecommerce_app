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


class BlogpostsView(ListView):
    model = Blogpost
    template_name = "blog/blogposts.html"
    context_object_name = "blogposts"
    paginate_by = 12

    def get_queryset(self):
        return Blogpost.objects.filter(is_published=True).order_by("created_at")


class BlogpostDetailView(DetailView):
    model = Blogpost
    template_name = "blog/blogpost_detail.html"
    context_object_name = "blogpost"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_published:
            obj.number_of_views += 1
            obj.save()
        return obj


class BlogpostCreateView(CreateView):
    model = Blogpost
    fields = ["title", "author", "content", "preview", "is_published",]
    template_name = "blog/blogpost_form.html"
    success_url = reverse_lazy("blog:main")


class BlogpostUpdateView(UpdateView):
    model = Blogpost
    fields = ["title", "author", "content", "preview", "is_published",]
    template_name = "blog/blogpost_form.html"
    success_url = reverse_lazy("blog:blogpost_detail")


class BlogpostDeleteView(DeleteView):
    model = Blogpost
    template_name = "blog/blogpost_confirm_delete.html"
    success_url = reverse_lazy("blog:blogpost_main")

