from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from django.conf import settings

class Article(models.Model):
    title = models.CharField(max_length=150)
    title_ru = models.CharField(max_length=150)
    title_uz = models.CharField(max_length=150)
    summary = models.CharField(max_length=200, blank=True)
    summary_ru = models.CharField(max_length=200, blank=True)
    summary_uz = models.CharField(max_length=200, blank=True)
    body = models.TextField(null=True, blank=True)
    body_ru = models.TextField(null=True, blank=True)
    body_uz = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='images/', blank=True)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', args=[str(self.id)])


class Comment(models.Model):
    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)