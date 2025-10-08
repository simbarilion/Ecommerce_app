from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView

from .forms import FeedbackForm

from .models import Product, Contacts, MessageFeedback


class HomeView(ListView):
    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"
    paginate_by = 6


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"


class ContactsView(FormView):
    # model = Contacts
    form_class = FeedbackForm
    template_name = "catalog/contacts.html"
    success_url = reverse_lazy("catalog:contacts")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["contacts"] = Contacts.objects.last()
        return context

    def form_valid(self, form):
        feedback = form.save()
        messages.success(self.request, f"Спасибо, {feedback.name}! Ваше сообщение получено")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Пожалуйста, заполните все поля")
        return super().form_invalid(form)
