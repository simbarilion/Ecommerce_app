from django.urls import path

# from blog.views import BlogpostListView, BlogpostDetailView, BlogpostCreateView, BlogpostUpdateView, BlogpostDeleteView, \
#     blogpost_search_view

app_name = "blog"

urlpatterns = [
    # Публичные маршруты
    # path("main/",
    #      BlogpostListView.as_view(template_name="blog/main.html", limit=6,),
    #      name="blog_main"),
    # path("blogposts/",
    #      BlogpostListView.as_view(template_name="blog/blogposts.html", paginate_by =12),
    #      name="blogposts"),
    # path("blogposts/<int:pk>/",
    #      BlogpostDetailView.as_view(template_name="blog/blogposts_detail.html"),
    #      name="blogposts_detail"),
    # # Маршрты для редактора
    # path("blogposts_editor/",
    #      BlogpostListView.as_view(template_name="blog/blogpost_list.html", paginate_by =50),
    #      name="blogpost_list"),
    # path("blogposts_editor/<int:pk>/",
    #      BlogpostDetailView.as_view(template_name="blog/blogpost_list_detail.html"),
    #      name="blogpost_list_detail"),
    # path("blogposts_editor/create/",
    #      BlogpostCreateView.as_view(),
    #      name="blogpost_create"),
    # path("blogposts_editor/<int:pk>/update/",
    #      BlogpostUpdateView.as_view(),
    #      name="blogpost_update"),
    # path("blogposts_editor/<int:pk>/delete/",
    #      BlogpostDeleteView.as_view(),
    #      name="blogpost_delete"),
    # path("search/", blogpost_search_view, name="blogpost_search"),
]