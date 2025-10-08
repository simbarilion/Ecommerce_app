from django.urls import path

from blog.views import BlogpostsView, BlogpostDetailView, BlogpostCreateView, BlogpostUpdateView, BlogMainView


app_name = "blog"

urlpatterns = [
    path("main/", BlogMainView.as_view(), name="blog_main"),
    path("blogposts/", BlogpostsView.as_view(), name="blogposts"),
    path("blogpost/<int:pk>/", BlogpostDetailView.as_view(), name="blogpost_detail"),
    path("blogpost_create/", BlogpostCreateView.as_view(), name="blogpost_create"),
    path("blogpost_update/", BlogpostUpdateView.as_view(), name="blogpost_update"),
    path("blogpost_delete/", BlogpostUpdateView.as_view(), name="blogpost_delete"),
]