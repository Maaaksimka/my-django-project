
from django.views.generic import ListView

from blogapp.models import Article


class BasedView(ListView):
    queryset = (
        Article.objects
        .select_related("author", "category")
        .prefetch_related("tags")
        .defer("content")
    )