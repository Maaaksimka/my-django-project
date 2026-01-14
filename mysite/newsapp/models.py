from django.db import models
from django.urls import reverse


class Article(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    body = models.TextField(blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse('newsapp:article', kwargs={'pk': self.pk})