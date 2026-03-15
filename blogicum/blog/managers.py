from django.db import models
from django.db.models import Count
from django.db.models.functions import Coalesce
from django.utils import timezone


class PostMethodsMixin:
    def with_comment_counts(self) -> 'PostQueryset':
        return self.annotate(comment_count=Coalesce(Count("comments"), 0))

    def published(self) -> 'PostQueryset':
        return self.select_related('category').filter(pub_date__lte=timezone.now(), is_published__exact=True,
                                                      category__is_published__exact=True)


class PostQueryset(models.QuerySet, PostMethodsMixin):
    pass


class PostManager(models.Manager, PostMethodsMixin):
    def get_queryset(self):
        return PostQueryset(self.model, using=self._db)
