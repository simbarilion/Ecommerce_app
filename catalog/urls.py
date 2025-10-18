from django.urls import path
from catalog.views import ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView, \
    ProductDeleteView, ContactsView, product_search_view


app_name = "catalog"


urlpatterns = [
    path("home/", ProductListView.as_view(), name="home"),
    path("search/", product_search_view, name="product_search"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path("create/", ProductCreateView.as_view(), name="product_create"),
    path("product/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("product/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
]
