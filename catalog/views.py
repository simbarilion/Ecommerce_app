import re
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView

from .forms import FeedbackForm, ProductForm, ProductModeratorForm

from .models import Product, Contacts
from .utils import is_moderator


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
        """Возвращает все опубликованные товары или товары по категории, если передан параметр category_id.
           Если позьзователь авторизован, также возвращает товары на модерации"""
        queryset = super().get_queryset()
        category_id = self.request.GET.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        user = self.request.user
        if user.is_authenticated:
            if is_moderator(user):
                queryset = queryset.filter(status__in=["published", "moderation", "archived"])
            else:
                queryset = queryset.filter(
                    Q(status="published") |
                    Q(status="moderation", owner=user)
                )
        else:
            queryset = queryset.filter(status="published")

        return queryset


class ProductDetailView(DetailView):
    """Представление для отдельного товара"""
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"

    def get_object(self, queryset=None):
        """Показывает товар, если он опубликован или если пользователь авторизован"""
        obj = super().get_object(queryset)
        user = self.request.user

        if user.is_authenticated:
            if is_moderator(user):
                if obj.status not in ["published", "moderation", "archived"]:
                    raise Http404("Товар недоступен")
            else:
                if obj.status == "moderation" and obj.owner != user:
                    raise Http404("Товар недоступен")
                if obj.status == "archived" or obj.status not in ["published", "moderation"]:
                    raise Http404("Товар недоступен")
                if obj.status not in ["published", "moderation", "archived"]:
                    raise Http404("Товар недоступен")
        else:
            if obj.status != "published":
                raise Http404("Товар недоступен")

        return obj


class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Представление для создания карточки товара"""
    model = Product
    template_name = "catalog/product_form.html"
    form_class = ProductForm
    context_object_name = "product"
    permission_required = "catalog.add_product"

    def form_valid(self, form):
        """Присваивает текущего авторизованного пользователя как владельца товара,
           устанавливает статус 'moderation'"""
        form.instance.owner = self.request.user
        form.instance.status = "moderation"
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        """Запрещает модераторам создавать товары"""
        user = request.user
        if is_moderator(user):
            raise PermissionDenied("Модераторам запрещено создавать товары")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """При успешном создании карточки товара возвращает на страницу просмотра товара"""
        return reverse_lazy("catalog:home")


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования карточки товара"""
    model = Product
    template_name = "catalog/product_form.html"
    context_object_name = "product"


    def form_valid(self, form):
        """Устанавливает при редактировании статус товара 'moderation'"""
        user = self.request.user
        obj = self.get_object()
        if obj.owner == user:
            form.instance.status = "moderation"
        return super().form_valid(form)

    def get_object(self, queryset=None):
        """Возвращает объект только если пользователь — владелец"""
        if not hasattr(self, "_cached_object"):
            self._cached_object = super().get_object(queryset)
            user = self.request.user

            if self._cached_object.owner != user and not is_moderator(user):
                raise PermissionDenied("Вы не можете редактировать чужой товар")
        return self._cached_object

    def get_form_class(self):
        """Выбирает форму в зависимости от пользователя"""
        user = self.request.user
        obj = self.get_object()

        if is_moderator(user) and obj.owner != user:
            return ProductModeratorForm
        return ProductForm

    def handle_no_permission(self):
        """Если пользователь не авторизован, возвращает HTTP-ответ об отстутсвии прав для редактирования товара"""
        if not self.request.user.is_authenticated:
            return redirect("users:login")
        raise PermissionDenied("У вас нет прав для редактирования товара")

    def get_success_url(self):
        """При успешном редактировании карточки товара возвращает на страницу просмотра товара"""
        return reverse_lazy("catalog:product_detail", kwargs={"pk": self.object.pk})


class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Представление для удаления карточки товара"""
    model = Product
    template_name = "catalog/product_delete.html"
    context_object_name = "product"
    success_url = reverse_lazy("catalog:home")
    permission_required = "catalog.delete_product"


    def get_object(self, queryset=None):
        """Возвращает объект только если пользователь — владелец"""
        obj = super().get_object(queryset)
        user = self.request.user

        if obj.owner != user and not is_moderator(user):
            raise PermissionDenied("Вы не можете удалить чужой товар")
        return obj

    def handle_no_permission(self):
        """Если пользователь не авторизован, возвращает HTTP-ответ об отстутсвии прав для удаления товара"""
        if not self.request.user.is_authenticated:
            return redirect("users:login")
        raise PermissionDenied("У вас нет прав для удаления товара")

    def delete(self, request, *args, **kwargs):
        """Помечает товар как 'archived' вместо физического удаления"""
        obj = self.get_object()
        obj.status = "archived"
        obj.save()
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
        """Добавляет сообщение об ошибке, возвращает пользователя на страницу с формой и показывает ошибки валидации"""
        messages.error(self.request, "Пожалуйста, заполните все поля")
        return super().form_invalid(form)


def product_search_view(request):
    """Осуществляет поисковый запрос товаров"""
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
