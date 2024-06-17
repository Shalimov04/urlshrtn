import uuid

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .form_validators import validate_url


class OuterUrl(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    url = models.TextField(max_length=256, validators=[validate_url], verbose_name='URL')
    slug = models.TextField(max_length=256, unique=True, blank=True, verbose_name='Идентификатор')

    def __str__(self):
        return str(self.url)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())[:32]
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'


class ShortenedUrl(models.Model):
    outer_url = models.ForeignKey(OuterUrl, on_delete=models.CASCADE)
    path = models.TextField(max_length=128, unique=True, verbose_name='Сокращенная ссылка')
    description = models.TextField(max_length=64, null=True, blank=True, verbose_name='Описание')

    def __str__(self):
        return str(self.path)

    class Meta:
        verbose_name = 'Сокращенная ссылка'
        verbose_name_plural = 'Сокращенные ссылки'


class Conversion(models.Model):
    shortened_url = models.ForeignKey(ShortenedUrl, on_delete=models.CASCADE)
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now=False)

    class Meta:
        verbose_name = 'Переход'
        verbose_name_plural = 'Переходы'
