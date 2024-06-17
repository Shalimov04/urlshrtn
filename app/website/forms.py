import random
import string

from django import forms
from django.forms.widgets import DateInput
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import OuterUrl, ShortenedUrl
from .form_validators import validate_url


def validate_unique_path(value):
    if ShortenedUrl.objects.filter(path=value).exists():
        raise ValidationError(f"Сокращенная ссылка с путем '{value}' уже существует!")


class OuterUrlForm(forms.Form):
    url = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ссылка для перенаправления'}),
        validators=[validate_url]
    )
    path = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Сокращенный путь'}),
        validators=[validate_unique_path]
    )

    def __init__(self, *args, **kwargs):
        super(OuterUrlForm, self).__init__(*args, **kwargs)

        default_path = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=6))
        self.fields['path'].initial = default_path

    def save(self, commit=False, user=None):
        outer_url_instance, created = OuterUrl.objects.get_or_create(
            user=user,
            url=self.cleaned_data['url'],
        )
        if commit:
            outer_url_instance.save()

        shortened_url_instance = ShortenedUrl(
            path=self.cleaned_data['path'],
            outer_url=outer_url_instance,
        )
        if commit:
            shortened_url_instance.save()

        return shortened_url_instance, outer_url_instance


class ShortenedUrlForm(forms.ModelForm):
    class Meta:
        model = ShortenedUrl
        fields = ['path', 'description']
        widgets = {
            'path': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Сокращенный путь'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
        }

    def __init__(self, *args, **kwargs):
        super(ShortenedUrlForm, self).__init__(*args, **kwargs)
        default_path = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=6))
        self.fields['path'].initial = default_path


class StatsChoiceForm(forms.Form):
    plot_type = forms.ChoiceField(
        label='Тип диаграммы',
        choices=[
            ('PieChart', 'Круговая диаграмма'),
            ('BarChart', 'Столбчатая диаграмма')
        ],
        required=False,
        widget=forms.Select(attrs={'id': 'formOption', 'class': 'input'})
    )

    date_start = forms.DateField(
        label='Начало диапазона',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
        input_formats=['%Y-%m-%d'],
        initial=date.today(),
        required=False,
    )

    date_end = forms.DateField(
        label='Конец диапазона',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
        input_formats=['%Y-%m-%d'],
        initial=date.today(),
        required=False,
    )

    def __init__(self, *args, min_date=None, max_date=None, **kwargs):
        self.user = kwargs.pop('user', None)
        super(StatsChoiceForm, self).__init__(*args, **kwargs)

        self.fields['date_start'].widget.attrs['min'] = min_date
        self.fields['date_start'].widget.attrs['max'] = max_date

        self.fields['date_end'].widget.attrs['min'] = min_date
        self.fields['date_end'].widget.attrs['max'] = max_date

    def get_choices(self):
        if not self.user:
            return [(option['slug'], option['url']) for option in
                    OuterUrl.objects.filter().values('url', 'slug').order_by('id')]
        return [(option['slug'], option['url']) for option in
                OuterUrl.objects.filter(user=self.user).values('url', 'slug').order_by('id')]
