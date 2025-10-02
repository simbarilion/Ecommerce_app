from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import Product, Contacts, MessageFeedback


def home(request):
    products = Product.objects.order_by("created_at")
    return render(request, "catalog/home.html", {"products": products})


def contacts(request):
    contacts = Contacts.objects.last()
    return render(request, "catalog/contacts.html", {"contacts": contacts})


def feedback(request):
    post_data = request.POST
    if post_data:
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        message = request.POST.get("message")
        if not name or not phone or not message:
            messages.error(request, "Пожалуйста, заполните все поля")
            return redirect(reverse("catalog:contacts"))
        message_feedback = MessageFeedback.objects.get_or_create(
            name=name,
            phone=phone,
            message=message
        )
        print(message_feedback, name, phone, message)
        messages.success(request, f"Спасибо, {name}! Ваше сообщение получено")
        return redirect(reverse("catalog:contacts"))
    return redirect(reverse("catalog:contacts"))


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "catalog/product_detail.html", {"product": product})
