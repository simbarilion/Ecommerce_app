import json
import re

from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
from django.http import Http404
from fuzzywuzzy import fuzz

from catalog.models import Product


def is_moderator(user):
    """Проверяет, состоит ли пользователь в группе модераторов"""
    return user.is_superuser or user.groups.filter(name="products_moderator").exists()


def get_visible_products_for_user(user):
    """
    Возвращает все опубликованные товары.
    Если пользователь авторизован и продавец, возвращает все опубликованные товары и товары продавца на модерации.
    Если пользователь - модератор товаров, возвращает все опубликованные товары, товары на модерации и в архиве
    """
    queryset = Product.objects.all()
    if user.is_authenticated:
        if is_moderator(user):
            return queryset.filter(status__in=["published", "moderation", "archived"])
        else:
            return queryset.filter(Q(status="published") | Q(status="moderation", owner=user))
    return queryset.filter(status="published")


def get_products_by_category(category_id, user):
    """
    Возвращает список товаров для указанной категории с учётом прав пользователя.
    Если category_id не указан, возвращает все доступные пользователю товары.
    """
    queryset = get_visible_products_for_user(user)
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    return queryset


def get_cached_products_by_category(category_id, user, timeout=60*15):
    """Возвращает кэшированные товары для категории с учётом пользователя"""
    cache_key = f"products_user_{user.id if user.is_authenticated else 'anon'}_cat_{category_id or 'all'}"
    cached_ids = cache.get(cache_key)
    if cached_ids is not None:
        return Product.objects.filter(id__in=cached_ids)

    queryset = get_products_by_category(category_id, user)
    ids = list(queryset.values_list("id", flat=True))
    cache.set(cache_key, ids, timeout)
    return queryset


def can_user_view_product(user, product):
    """
    Проверяет, имеет ли пользователь право просматривать указанный товар.
    Возбуждается Http404: 'Товар недоступен', если доступ запрещён
    """
    if user.is_authenticated:
        if is_moderator(user):
            if product.status not in ["published", "moderation", "archived"]:
                raise Http404("Товар недоступен")
            else:
                if product.status == "moderation" and product.owner != user:
                    raise Http404("Товар недоступен")
                if product.status == "archived" or product.status not in ["published", "moderation"]:
                    raise Http404("Товар недоступен")
        else:
            if product.status != "published":
                raise Http404("Товар недоступен")


def check_user_can_create_product(user):
    """Проверяет, имеет ли пользователь право создавать товар"""
    if is_moderator(user):
        raise PermissionDenied("Модераторам запрещено создавать товары")


def check_user_can_edit_product(user, product):
    """Проверяет, имеет ли пользователь право редактировать товар"""
    if is_moderator(user):
        return
    if product.owner == user:
        if product.status in ["published", "moderation"]:
            return
    raise PermissionDenied("Вы не можете редактировать чужой товар")


def update_product_status_on_edit(product, user, form):
    """
    Обновляет товар при редактировании пользователем.
    Если редактирует владелец — статус становится 'moderation'
    """
    if product.owner == user:
        form.instance.status = "moderation"


def check_user_can_delete_product(user, product):
    """Проверяет, имеет ли пользователь право поместить товар в архив"""
    if product.owner != user and not is_moderator(user):
        raise PermissionDenied("Вы не можете удалить чужой товар")


def archive_product(product, user):
    """Устанавливает статус 'archived' для товара"""
    check_user_can_delete_product(user, product)
    product.status = "archived"
    product.save(update_fields=["status"])


def search_products(query: str, cache_timeout: int = 60*5) -> QuerySet:
    """
    Возвращает QuerySet товаров, соответствующих поисковому запросу.
    Разбивает строку на слова и ищет их в name, brief_description и description.
    """
    if not query:
        return Product.objects.none()

    cache_key = f"search_products:{query.lower()}"
    cached_ids = cache.get(cache_key)
    if cached_ids is not None:
        return Product.objects.filter(id__in=cached_ids)

    keywords = re.findall(r'\w+', query)
    q_objects = Q()
    for word in keywords:
        q_objects &= (Q(name__icontains=word) |
                      Q(brief_description__icontains=word) |
                      Q(description__icontains=word))

    queryset = Product.objects.filter(q_objects)

    ids = list(queryset.values_list("id", flat=True))
    cache.set(cache_key, ids, cache_timeout)

    return queryset


class SpamChecker:
    """Проверяет текстовые поля на запрещённые слова"""

    THRESHOLD = 85
    SPAM_WORDS_PATH = "catalog/data/spam_words.json"


    def __init__(self):
        self.spam_words = self._load_spam_words(self.SPAM_WORDS_PATH)
        self.pattern = self._build_pattern(self.spam_words)


    @staticmethod
    def _load_spam_words(filepath: str) -> list:
        """Загружает список запрещённых слов из JSON файла"""
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            return [word.lower() for word in data.get("spam_words", [])]
        except FileNotFoundError:
            return []


    @staticmethod
    def _build_pattern(words: list):
        """Создаёт паттерн для поиска запрещённых слов"""
        escaped = [re.escape(word) for word in words]
        return re.compile(r'(' + "|".join(escaped) + r')\w*', re.IGNORECASE)


    def check_text(self, text: str) -> None:
        """Проверяет текст на спам и запрещённые слова"""
        if not text:
            return

        text_lower = text.lower()
        if self.pattern.search(text_lower):
            raise ValueError("Текст содержит запрещённые слова")

        for spam in self.spam_words:
            if fuzz.partial_ratio(spam, text_lower) >= self.THRESHOLD:
                raise ValueError(f"Запрещённые слова: '{spam}'")
