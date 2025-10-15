from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView

from .forms import FeedbackForm

from .models import Product, Contacts


class HomeView(ListView):
    """Представление для домашней страницы"""
    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self):
        return Product.objects.filter(status="published").order_by("created_at")


class ProductDetailView(DetailView):
    """Представление для отдельного товара"""
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"


class ProductCreateView(CreateView):
    """Представление для создания статьи Блога"""
    model = Product
    template_name = "catalog/product_form.html"
    form_class = ProductForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = "moderation"
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("catalog:#")


class ProductUpdateView(UpdateView):
    """Представление для редактирования статьи Блога"""
    model = Product
    template_name = "catalog/product_form.html"
    form_class = ProductForm
    slug_field = "slug"

    def get_success_url(self):
        return reverse_lazy("catalog:product_detail", kwargs={"slug": "slug"})

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = "moderation"
        return super().form_valid(form)


class ProductDeleteView(DeleteView):
    """Представление для удаления статьи Блога"""
    model = Product
    template_name = "catalog/product_delete.html"
    success_url = reverse_lazy("catalog:home")
    form_class = ProductForm

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.seller



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
