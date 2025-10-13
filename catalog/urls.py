from django.urls import path
from catalog.views import HomeView, ProductDetailView, ContactsView

app_name = "catalog"

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
]
