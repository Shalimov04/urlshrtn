from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from .forms import OuterUrlForm, ShortenedUrlForm
from .models import OuterUrl, ShortenedUrl


@login_required
def create_outer_url(request):
    if request.method == 'POST':
        form = OuterUrlForm(request.POST)  # Передаем данные из запроса в форму
        if form.is_valid():
            try:
                shortened_url, outer_url = form.save(commit=True, user=request.user)
                return redirect('/')
            except IntegrityError:
                form = OuterUrlForm()
        else:
            print(form.errors)  # Вывод ошибок формы для диагностики
    else:
        form = OuterUrlForm()
    return render(request, 'add_outer_url.html', {'form': form})


@login_required
def create_shortened_url(request, ou_slug):
    try:
        outer_url = OuterUrl.objects.get(slug=ou_slug)
    except Exception as e:
        return redirect('/')  # TODO: обработка исключения
    if request.method == 'POST':
        form = ShortenedUrlForm(request.POST)
        if form.is_valid():
            shortened_url = form.save(commit=False)
            shortened_url.outer_url = outer_url
            shortened_url.save()
            return redirect('/')
    else:
        form = ShortenedUrlForm()
    return render(request, 'add_inner_url.html', {'form': form})


@login_required
def edit_shortened_url(request, ou_slug, url_id):
    try:
        outer_url = OuterUrl.objects.get(slug=ou_slug)
    except OuterUrl.DoesNotExist:
        return redirect('/')

    try:
        shortened_url = ShortenedUrl.objects.get(id=url_id, outer_url=outer_url)
    except ShortenedUrl.DoesNotExist:
        return redirect('/')

    if request.method == 'POST':
        form = ShortenedUrlForm(request.POST, instance=shortened_url)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = ShortenedUrlForm(instance=shortened_url)

    return render(request, 'edit_inner_url.html', {'form': form})
