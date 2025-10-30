from abc import ABC, abstractmethod

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView

from .forms import FeedbackForm, ProductForm, ProductModeratorForm

from .models import Product, Contacts
from .services.product_service import is_moderator, get_cached_products, can_user_view_product, \
    check_user_can_create_product, check_user_can_edit_product, update_product_status_on_edit, \
    check_user_can_delete_product, archive_product, search_products, get_visible_products_for_user, \
    invalidate_product_cache


class BaseProductListView(ListView, ABC):
    """Абстрактное базовое представление для списка товаров"""
    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"
    paginate_by = 9


    def get_context_data(self, **kwargs):
        """Добавляет поиск по товарам в контекст"""
        context = super().get_context_data(**kwargs)
        context["search_type"] = "product"
        return context


    @abstractmethod
    def get_queryset(self):
        """Базовый метод получения товаров для переопределения в дочерних классах"""
        pass


class ProductListView(BaseProductListView):
    """Представление для отображения всех доступных товаров"""

    def get_queryset(self):
        """Возвращает кэшированный список всех товаров с учётом прав пользователя"""
        return get_cached_products(self.request.user)


class CategoryProductListView(BaseProductListView):
    """Представление для отображения всех доступных товаров выбранной категории"""

    def get_context_data(self, **kwargs):
        """Добавляет категорию товаров в контекст"""
        context = super().get_context_data(**kwargs)
        context["current_category_id"] = self.request.GET.get("category_id")
        return context


    def get_queryset(self):
        """Возвращает товары выбранной категории с учётом прав пользователя"""
        category_id = self.kwargs.get("category_id")
        return get_cached_products(self.request.user, category_id)


@method_decorator(cache_page(60 * 15), name="dispatch")
class ProductDetailView(DetailView):
    """Представление для отдельного товара"""
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"


    def get_object(self, queryset=None):
        """
        Показывает товар, если он опубликован или если пользователь
        имеет права на просмотр неопубликованных товаров
        """
        product = super().get_object(queryset)
        can_user_view_product(self.request.user, product)
        return product


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания карточки товара"""
    model = Product
    template_name = "catalog/product_form.html"
    form_class = ProductForm
    context_object_name = "product"


    def get_context_data(self, **kwargs):
        """Определяет в контексте с объект товара"""
        context = super().get_context_data(**kwargs)
        context["obj"] = None
        return context


    def form_valid(self, form):
        """
        Присваивает текущего авторизованного пользователя как владельца товара,
        устанавливает статус 'moderation'
        """
        form.instance.owner = self.request.user
        form.instance.status = "moderation"
        response = super().form_valid(form)

        invalidate_product_cache()
        return response


    def dispatch(self, request, *args, **kwargs):
        """Запрещает модераторам создавать товары"""
        check_user_can_create_product(request.user)
        return super().dispatch(request, *args, **kwargs)


    def get_success_url(self):
        """При успешном создании карточки товара возвращает на страницу просмотра товара"""
        return reverse_lazy("catalog:home")


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования карточки товара"""
    model = Product
    template_name = "catalog/product_form.html"
    context_object_name = "product"


    def get_context_data(self, **kwargs):
        """Возвращает контекст с объектом товара"""
        context = super().get_context_data(**kwargs)
        context["obj"] = self.object
        return context


    def get_object(self, queryset=None):
        """Возвращает объект только если пользователь — владелец"""
        if not hasattr(self, "_cached_object"):
            self._cached_object = super().get_object(queryset)
            check_user_can_edit_product(self.request.user, self._cached_object)
        return self._cached_object


    def form_valid(self, form):
        """Устанавливает при редактировании статус товара 'moderation'"""
        product = self.get_object()
        update_product_status_on_edit(product, self.request.user, form)
        response = super().form_valid(form)

        invalidate_product_cache(product.category_id)
        return response


    def get_form_class(self):
        """Выбирает форму в зависимости от статуса пользователя"""
        user = self.request.user
        obj = self.get_object()

        if is_moderator(user) and obj.owner != user:
            return ProductModeratorForm
        return ProductForm


    def handle_no_permission(self):
        """Если пользователь не авторизован, перенаправляет на страницу авторизации"""
        if not self.request.user.is_authenticated:
            return redirect("users:login")
        raise PermissionDenied("У вас нет прав для редактирования товара")


    def get_success_url(self):
        """При успешном редактировании карточки товара возвращает на страницу просмотра товара"""
        return reverse_lazy("catalog:product_detail", kwargs={"pk": self.object.pk})


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Представление для удаления карточки товара"""
    model = Product
    template_name = "catalog/product_delete.html"
    context_object_name = "product"
    success_url = reverse_lazy("catalog:home")


    def get_object(self, queryset=None):
        """Возвращает объект только если пользователь — владелец или имеет права модератора"""
        product = super().get_object(queryset)
        check_user_can_delete_product(self.request.user, product)
        return product


    def handle_no_permission(self):
        """
        Если пользователь не авторизован, возвращает HTTP-ответ
        об отстутсвии прав для удаления товара
        """
        if not self.request.user.is_authenticated:
            return redirect("users:login")
        raise PermissionDenied("У вас нет прав для удаления товара")


    def post(self, request, *args, **kwargs):
        """Помечает товар как 'archived' вместо физического удаления"""
        product = self.get_object()
        archive_product(product, request.user)

        invalidate_product_cache(product.category_id)
        return HttpResponseRedirect(self.success_url)


class ContactsView(FormView):
    """Представление для страницы Контакты"""
    form_class = FeedbackForm
    template_name = "catalog/contacts.html"
    success_url = reverse_lazy("catalog:contacts")

    def get_context_data(self, **kwargs):
        """Добавляет последнюю сохраненную контактную информацию в контекст"""
        context = super().get_context_data(**kwargs)
        context["contacts"] = Contacts.objects.last()
        return context

    def form_valid(self, form):
        """Сохраняет данные формы в базу данных, добавляет 'флеш-сообщение'"""
        feedback = form.save()
        messages.success(self.request, f"Спасибо, {feedback.name}! Ваше сообщение получено")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Добавляет сообщение об ошибке, возвращает пользователя на страницу с формой
        и показывает ошибки валидации
        """
        messages.error(self.request, "Пожалуйста, заполните все поля")
        return super().form_invalid(form)


def product_search_view(request):
    """Осуществляет поисковый запрос товаров"""
    query = request.GET.get("q", "").strip()
    products = search_products(query)

    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "search_type": "product",
        "query": query,
        "page_obj": page_obj,
    }
    return render(request, "catalog/product_search.html", context)
