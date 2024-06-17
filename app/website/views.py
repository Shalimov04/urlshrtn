import plotly.express as px
import pandas as pd
import qrcode
from io import BytesIO
import base64

from .models import OuterUrl, ShortenedUrl, Conversion
from .methods import get_client_ip, get_user_agent
from .forms import OuterUrlForm, ShortenedUrlForm, StatsChoiceForm
from .plots import plot_conversions, plot_data
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.db.models import F
from datetime import datetime, date, timedelta
from pandas import json_normalize


def forward(request, path):
    try:
        obj = ShortenedUrl.objects.get(path=path)
        url = obj.outer_url.url
        Conversion.objects.create(
            shortened_url=obj,
            timestamp=datetime.now(),
            data={
                "ip": get_client_ip(request),
                # "device": get_device(request)
            } | get_user_agent(request)
        )
        return redirect(url)
    except Exception as e:
        print(e)
        return HttpResponse('Несуществующий путь! <br> <a href="/">Назад</a>')


@login_required
def main_page(request):
    context = {'urls': {}}

    for outer_url in OuterUrl.objects.filter(user=request.user):
        context['urls'][outer_url] = {}
        context['add_outer_url_form'] = OuterUrlForm()
        for shortened_url in ShortenedUrl.objects.filter(outer_url=outer_url):
            context['urls'][outer_url][shortened_url] = {
                'path': shortened_url.path,
                'stats': Conversion.objects.filter(shortened_url=shortened_url).count(),
            }

    return render(request, 'main.html', context)


@login_required
def plot_view(request, ou_slug=None, su_path=None):
    conversions = Conversion.objects.all()
    if ou_slug:
        try:
            outer_url = OuterUrl.objects.get(user=request.user, slug=ou_slug)
            conversions = conversions.filter(shortened_url__outer_url=outer_url)
        except Exception as e:
            return HttpResponse('Несуществующий url! <br> <a href="/">Назад</a>')
    if su_path:
        try:
            shortened_url = ShortenedUrl.objects.get(path=su_path)
            conversions = conversions.filter(shortened_url=shortened_url)
        except Exception as e:
            return HttpResponse('Несуществующий path! <br> <a href="/">Назад</a>')
    else:
        shortened_url = None
    try:
        plot_type, form = None, None
        form = StatsChoiceForm(
            request.POST,
            user=request.user,
            min_date=conversions.order_by('timestamp').earliest('id').timestamp.date,
            max_date=date.today(),
        )
        if form.is_valid():
            plot_type = form.cleaned_data['plot_type']
            min_date = form.cleaned_data['date_start']
            max_date = form.cleaned_data['date_end']

        conversions_json = plot_conversions(outer_url, shortened_url, min_date, max_date)
        data_plots = plot_data(
            outer_url=outer_url,
            shortened_url=shortened_url,
            cols=['device', 'browser', 'os'],
            plot_type=plot_type or None,
            min_date=min_date,
            max_date=max_date
        )
    except Exception as e:
        return render(request, 'plot_template.html', {'message': 'Отсутствуют данные о переходах!'})

    context = {
        'title': f'{plot_type or ""} {outer_url.url}',
        'plot_data': conversions_json,
        'data_plots': data_plots,
    }

    if form:
        context['form'] = form

    context |= {
        "total_conversions": conversions.count(),
        "daily_conversions": conversions.filter(timestamp__gte=datetime.now() - timedelta(days=1)).count(),
        "weekly_conversions": conversions.filter(timestamp__gte=datetime.now() - timedelta(weeks=1)).count(),
    }

    return render(request, 'plot_template.html', context)


@login_required
def get_qr(request, link):
    if link:
        try:
            shortened_url = ShortenedUrl.objects.get(path=link)
            url = shortened_url.path
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(request.build_absolute_uri(f'/{url}'))
            qr.make(fit=True)

            img = qr.make_image(fill='black', back_color='white')

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            img_data = f'data:image/png;base64,{img_base64}'

            return render(request, 'qr.html', {'qr': img_data, 'url': url})
        except ShortenedUrl.DoesNotExist:
            return HttpResponse('Несуществующий url! <br> <a href="/">Назад</a>')
    else:
        return HttpResponse('Отсутствует ссылка! <br> <a href="/">Назад</a>')


@login_required
def delete_shortened_url(request, su_path=None):
    try:
        ShortenedUrl.objects.get(path=su_path, outer_url__user=request.user).delete()
        return redirect('/')
    except Exception as e:
        return HttpResponse('Удаление невозможно! <br> <a href="/">Назад</a>')


@login_required
def delete_outer_url(request, ou_slug=None):
    try:
        OuterUrl.objects.get(slug=ou_slug, user=request.user).delete()
        return redirect('/')
    except Exception as e:
        return HttpResponse('Удаление невозможно! <br> <a href="/">Назад</a>')


@login_required
def download_excel(request, ou_slug=None, su_path=None):
    try:
        outer_url = OuterUrl.objects.filter(user=request.user, slug=ou_slug)
        if su_path:
            shortened_urls = [ShortenedUrl.objects.get(path=su_path)]
        else:
            if outer_url.exists():
                outer_url = outer_url.first()
                shortened_urls = ShortenedUrl.objects.filter(outer_url=outer_url)
        df = pd.DataFrame(
            Conversion.objects.filter(shortened_url__in=shortened_urls)
            .annotate(shortened_url_path=F('shortened_url__path'))
            .values()
        )
        df = pd.concat([df.drop(['data'], axis=1), json_normalize(df['data'])], axis=1)
        df['timestamp'] = df['timestamp'].dt.tz_localize(None)
        excel_file = BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        response = FileResponse(excel_file,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="statistics.xlsx"'
        return response
    except Exception as e:
        return HttpResponse(f'Ошибка\n {str(e)}! <br> <a href="/">Назад</a>')
