from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count

from .constants import AMOUNT_POSTS_ON_MAIN_PAGE
from .models import Post


def get_paginator(page_number, posts_list):
    paginator = Paginator(posts_list, AMOUNT_POSTS_ON_MAIN_PAGE)
    return paginator.get_page(page_number)


def get_queryset(
        manager=Post.objects,
        filters=True,
        with_comments=True
):
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
