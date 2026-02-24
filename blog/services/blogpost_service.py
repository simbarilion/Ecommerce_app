import re

from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
from django.http import Http404

from blog.models import Blogpost


def is_content_manager(user):
    """Проверяет, состоит ли пользователь в группе контент-менеджеров"""
    return user.is_superuser or user.groups.filter(name="content_manager").exists()


def get_visible_blogposts_for_user(user, template_name=None, limit=None, timeout=60*5):
    """
    Возвращает QuerySet статей блога, доступных для пользователя.
    :param user: текущий пользователь
    :param template_name: шаблон, чтобы фильтровать для главной страницы
    :param limit: максимальное количество записей
    :param timeout: срок жизни кэшированных данных
    """
    cache_key = f"visible_blogposts:{user.id if user.is_authenticated else 'anon'}:{template_name or 'all'}:{limit or 'all'}"
    cached_ids = cache.get(cache_key)
    if cached_ids is not None:
        return Blogpost.objects.filter(id__in=cached_ids).order_by("-created_at")

    queryset = Blogpost.objects.all().order_by("-created_at")
    if template_name == "blog/main.html":
        queryset = queryset.filter(status="published")
    else:
        if user.is_authenticated:
            if is_content_manager(user):
                queryset = queryset.filter(status__in=["published", "moderation", "archived"])
            else:
                queryset = queryset.filter(
                    Q(status="published") |
                    Q(status="moderation", author=user)
                )
        else:
            queryset = queryset.filter(status="published")

    if limit:
        return queryset[:limit]

    ids = list(queryset.values_list("id", flat=True))
    cache.set(cache_key, ids, timeout)
    return queryset


def can_user_view_blogpost(user, post):
    """
        Проверяет, имеет ли пользователь право просматривать указанную статью блога.
        Возбуждается Http404: 'Статья недоступна', если доступ запрещён
        """
    if is_content_manager(user):
        pass
    elif user.is_authenticated:
        if post.status == "moderation" and post.author != user:
            raise Http404("Статья недоступна")
        if post.status not in ["published", "moderation"]:
            raise Http404("Статья недоступна")
    else:
        if post.status != "published":
            raise Http404("Статья недоступна")

    if post.status == "published":
        post.number_of_views += 1
        post.save(update_fields=["number_of_views"])
    return post


def check_user_can_create_blogpost(user):
    """Проверяет, имеет ли пользователь право создавать статью блога"""
    if is_content_manager(user):
        raise PermissionDenied("Контент-менеджерам запрещено создавать статьи блога")


def update_blogpost_status_on_edit(post, user, form):
    """
        Обновляет статью блога при редактировании пользователем.
        Если редактирует автор — статус становится 'moderation'
        """
    if post.author == user:
        form.instance.status = "moderation"


def check_user_can_edit_blogpost(user, post):
    """Проверяет, имеет ли пользователь право редактировать статью юлога"""
    if is_content_manager(user):
        return
    if post.author == user:
        if post.status in ["published", "moderation"]:
            return
    raise PermissionDenied("Вы не можете редактировать чужую статью")


def check_user_can_delete_blogpost(user, post):
    """Проверяет, имеет ли пользователь право поместить статью блога в архив"""
    if post.author != user and not is_content_manager(user):
        raise PermissionDenied("Вы не можете удалить чужую статью")


def archive_blogpost(post, user):
    """Устанавливает статус 'archived' для статьи блога"""
    check_user_can_delete_blogpost(user, post)
    post.status = "archived"
    post.save(update_fields=["status"])


def search_blogposts(query: str, cache_timeout: int = 60*5) -> QuerySet:
    """
    Возвращает QuerySet товаров, соответствующих поисковому запросу.
    Разбивает строку на слова и ищет их в name, brief_description и description.
    """
    if not query:
        return Blogpost.objects.none()

    cache_key = f"search_posts:{query.lower()}"
    cached_ids = cache.get(cache_key)
    if cached_ids is not None:
        return Blogpost.objects.filter(id__in=cached_ids)

    keywords = re.findall(r'\w+', query)
    q_objects = Q()
    for word in keywords:
        q_objects |= (Q(title__icontains=word) | Q(content__icontains=word))

    queryset = Blogpost.objects.filter(q_objects, status="published").distinct()

    ids = list(queryset.values_list("id", flat=True))
    cache.set(cache_key, ids, cache_timeout)

    return queryset
