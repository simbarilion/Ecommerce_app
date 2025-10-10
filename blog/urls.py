from django.urls import path

from blog.views import BlogpostsView, BlogpostCreateView, BlogpostUpdateView, BlogMainView, \
    BlogpostDeleteView, BlogpostListView, BlogpostListDetailView, BlogpostsDetailView

app_name = "blog"

urlpatterns = [
    path("main/", BlogMainView.as_view(), name="blog_main"),
    path("blogposts/", BlogpostsView.as_view(), name="blogposts"),
    path("blogposts/<int:pk>/", BlogpostsDetailView.as_view(), name="blogposts_detail"),
    path("blogposts_editor/", BlogpostListView.as_view(), name="blogpost_list"),
    path("blogposts_editor/<int:pk>/", BlogpostListDetailView.as_view(), name="blogpost_list_detail"),
    path("blogposts_editor/create/", BlogpostCreateView.as_view(), name="blogpost_create"),
    path("blogposts_editor/<int:pk>/update/", BlogpostUpdateView.as_view(), name="blogpost_update"),
    path("blogposts_editor/<int:pk>/delete/", BlogpostDeleteView.as_view(), name="blogpost_delete"),
]