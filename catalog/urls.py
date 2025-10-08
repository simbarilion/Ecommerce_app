from django.urls import path
from catalog import views
from catalog.views import HomeView, ProductDetailView

app_name = "catalog"

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
    path("contacts/", views.contacts, name="contacts"),
    path("feedback/", views.feedback, name="feedback"),

]
