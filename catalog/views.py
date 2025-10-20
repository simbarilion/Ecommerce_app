import re

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView

from .forms import FeedbackForm, ProductForm

from .models import Product, Contacts, Category


class ProductListView(ListView):
    """Представление для домашней страницы и списка товаров"""
    model = Product
    context_object_name = "products"
    paginate_by = 9
    template_name = "catalog/home.html"


    def get_context_data(self, **kwargs):
        """Добавляет список всех категорий в контекст"""
        context = super().get_context_data(**kwargs)
        context["current_category_id"] = self.request.GET.get("category_id")
        context["search_type"] = "product"
        return context


    def get_queryset(self):
        """Возвращает все товары или товары по категории, если передан параметр category_id"""
        queryset = super().get_queryset()
        category_id = self.request.GET.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class ProductDetailView(DetailView):
    """Представление для отдельного товара"""
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"


class ProductCreateView(CreateView):
    """Представление для создания карточки товара"""
    model = Product
    template_name = "catalog/product_form.html"
    form_class = ProductForm
    context_object_name = "product"

    def get_success_url(self):
        return reverse_lazy("catalog:home")


class ProductUpdateView(UpdateView):
    """Представление для редактирования карточки товара"""
    model = Product
    template_name = "catalog/product_form.html"
    form_class = ProductForm
    context_object_name = "product"

    def get_success_url(self):
        return reverse_lazy("catalog:product_detail", kwargs={"pk": self.object.pk})


class ProductDeleteView(DeleteView):
    """Представление для удаления карточки товара"""
    model = Product
    template_name = "catalog/product_delete.html"
    context_object_name = "product"
    success_url = reverse_lazy("catalog:home")


class ContactsView(FormView):
    """Представление для страницы Контакты"""
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


def product_search_view(request):
    query = request.GET.get("q", "").strip()
    products = []

    if query:
        keywords = re.findall(r'\w+', query)

        q_objects = Q()
        for word in keywords:
            q_objects &= (Q(name__icontains=word) |
                          Q(brief_description__icontains=word) |
                          Q(description__icontains=word))

        products = Product.objects.filter(q_objects)

    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "search_type": "product",
        "query": query,
        "page_obj": page_obj,
    }
    return render(request, "catalog/product_search.html", context)
