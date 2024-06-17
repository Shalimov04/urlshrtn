import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

from .models import OuterUrl, ShortenedUrl, Conversion
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate


def plot_conversions(outer_url: OuterUrl = None, shortened_url: ShortenedUrl = None, min_date=None, max_date=None):
    labels = {
        'Date': 'дата',
        'Conversions': 'переходы',
        'ShortenedUrl': 'сокращенная ссылка',
    }

    data = {'OuterUrl': [], 'ShortenedUrl': [], 'Date': [], 'Conversions': []}
    df = pd.DataFrame(data)
    if shortened_url:
        shortened_urls = [shortened_url]
    elif outer_url:
        shortened_urls = outer_url.shortenedurl_set.all()
    else:
        return {}

    for shortened_url in shortened_urls:
        conversions_by_day = shortened_url.conversion_set
        if min_date and max_date:
            conversions_by_day = conversions_by_day.filter(
                timestamp__gte=min_date,
                timestamp__lte=max_date
            )

        conversions_by_day = conversions_by_day.annotate(date=TruncDate('timestamp')) \
            .values('date').annotate(total_conversions=Count('id')).order_by('date')
        temp_data = {'OuterUrl': [outer_url.url] * len(conversions_by_day),
                     'ShortenedUrl': [shortened_url.path] * len(conversions_by_day),
                     'Date': [item['date'] for item in conversions_by_day],
                     'Conversions': [item['total_conversions'] for item in conversions_by_day]}
        temp_df = pd.DataFrame(temp_data)
        df = pd.concat([df, temp_df])

    result_df = df.groupby(['OuterUrl', 'ShortenedUrl', 'Date']).agg({'Conversions': 'sum'}).reset_index()
    result_df['Date'] = pd.to_datetime(result_df['Date'])
    result_df['Date'] = result_df['Date'].dt.strftime('%Y-%m-%d')
    fig = px.line(result_df, x="Date", y="Conversions", color='ShortenedUrl', markers=True, labels=labels)

    return fig.to_json()


def plot_data(outer_url: OuterUrl, shortened_url: ShortenedUrl = None, cols: list = None, plot_type: str = 'PieChart', min_date=None, max_date=None):
    labels = {
        'device': 'устройство',
        'count': 'переходов',
        'browser': 'браузер',
        'os': 'ОС',
    }

    if shortened_url:
        conversions = Conversion.objects.filter(shortened_url=shortened_url)
    elif outer_url:
        conversions = Conversion.objects.filter(shortened_url__outer_url=outer_url)
    else:
        return {}
    if min_date and max_date:
        conversions = conversions.filter(timestamp__gte=min_date, timestamp__lte=max_date)
    data_list = []

    for conversion in conversions:
        data = conversion.data
        data["timestamp"] = conversion.timestamp  # Добавляем временную метку к данным
        data_list.append(data)

    df = pd.DataFrame(data_list)
    if len(list(df.columns)) == 0:
        return {}

    if not cols:
        cols = list(df.columns)
        cols.remove('timestamp')

    charts = {}
    for col in cols:
        try:
            plot_df = df[col].value_counts().reset_index()
            plot_df.columns = [col, 'count']
            if plot_type == 'PieChart':
                fig = px.pie(plot_df, values='count', names=col, title=labels[col], labels=labels)
            elif plot_type == 'BarChart':
                fig = px.bar(plot_df, y='count', x=col, title=labels[col], labels=labels)
            else:
                fig = px.pie(plot_df, values='count', names=col, title=labels[col], labels=labels)

            charts[col] = fig.to_json()
        except Exception as e:
            pass

    return charts
