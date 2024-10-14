from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count

from .constants import AMOUNT_POSTS_ON_MAIN_PAGE
from .models import Post


def get_paginator(request, posts_list):
    """
    Отвечает за организацию постраничного вывода (пагинации) списка постов.
    """
    page_number = request.GET.get('page', 1)
    paginator = Paginator(posts_list, AMOUNT_POSTS_ON_MAIN_PAGE)
    return paginator.get_page(page_number)


def get_queryset(
        manager=Post.objects,
        filters=True,
        with_comments=True
):
    """
    Отвечает за создание и модификацию запроса (queryset)
    для получения постов из базы данных с нужными условиями и аннотациями.
    """
    queryset = manager.select_related('author', 'location', 'category')
    if filters:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lt=timezone.now(),
            category__is_published=True
        )
    if with_comments:
        queryset = queryset.annotate(comment_count=Count('comments'))
    return queryset.order_by('-pub_date')
