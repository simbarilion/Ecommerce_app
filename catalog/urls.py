from django.urls import path
from catalog.views import HomeView, ProductDetailView, ContactsView, ProductCreateView, ProductUpdateView, \
    ProductDeleteView

app_name = "catalog"

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
    path("home/create/", ProductCreateView.as_view(), name="product_create"),
    path("product/<slug:slug>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("product/<slug:slug>/delete/", ProductDeleteView.as_view(), name="product_delete"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
]
