from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contacts


def home(request):
    products = Product.objects.order_by("created_at")[:5]
    return render(request, "catalog/home.html", {"products": products})


def contacts(request):
    contacts = Contacts.objects.last()
    if request.method == "POST":
        name = request.POST.get("name")
        message = request.POST.get("message")
        return HttpResponse(f"Спасибо, {name}! Ваше сообщение получено.")
    return render(request, "catalog/contacts.html", {"contacts": contacts})
