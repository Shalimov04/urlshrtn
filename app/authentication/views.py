from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth.models import User
from .forms import UserLoginForm, RegisterForm


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.filter(username=username, password=password).first()
            if user:
                request.session['user_id'] = user.id
                return redirect('/')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = RegisterForm()

    return render(response, "register.html", {"form": form})


def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('login')