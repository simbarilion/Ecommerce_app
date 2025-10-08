from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/catalog/home/', permanent=False)),
    path("admin/", admin.site.urls),
    path("catalog/", include("catalog.urls", namespace="catalog")),
    path("blog/", include("blog.urls", namespace="blog")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
