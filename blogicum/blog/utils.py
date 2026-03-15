from django.core.paginator import Paginator
from django.utils.functional import cached_property


class OptimizedPaginator(Paginator):
    def __init__(self, object_list, per_page, count_func: callable, **kwargs):
        super().__init__(object_list, per_page, **kwargs)
        self.count_provider = count_func

    @cached_property
    def count(self):
        return self.count_provider()
