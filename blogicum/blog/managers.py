from django.db import models
from django.utils.timezone import now


class PostQuerySet(models.QuerySet):
    """
    QuerySet (разработанный для публикаций):
    Метод - join_related_data - служит для объединения данных,
    Метод - published - фильтровка публикаций.
    """

    def join_related_data(self):
        return self.select_related(
            'author',
            'category',
            'location'
        )

    def published(self):
        return self.filter(
            is_published=True,
            pub_date__lte=now(),
            category__is_published=True
        )


class PostManager(models.Manager):
    """
    Класс менеджер (разработанный менеджер для запросов публикаций):
    Метод - get_queryset - вызов класса PostQuerySet
    с методами join_related_data + published.
    """

    def get_queryset(self):
        return (
            PostQuerySet(self.model)
            .join_related_data()
            .published()
        )
