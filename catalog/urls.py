from django.urls import path
from catalog import views


app_name = "catalog"

urlpatterns = [
    path("home/", views.home, name="home"),
    path("contacts/", views.contacts, name="contacts"),
    path("feedback/", views.feedback, name="feedback"),
]
