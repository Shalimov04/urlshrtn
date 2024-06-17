"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from website import views
from website import form_views as form_views
from authentication.views import register
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.shortcuts import redirect


def logout_view(request):
    logout(request)
    return redirect('/')


urlpatterns = [
    path('<path>/', views.forward, name='forward'),
    path('accounts/register/', register, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/admin/', admin.site.urls),

    path('', views.main_page, name='main_page'),

    path('forms/create_outer_url/', form_views.create_outer_url, name='create_outer_url'),
    path('forms/create_shortened_url/<ou_slug>/', form_views.create_shortened_url, name='create_shortened_url'),
    path('forms/edit_shortened_url/<ou_slug>/<url_id>/', form_views.edit_shortened_url, name='edit_shortened_url'),

    path('tools/get_qr/<link>/', views.get_qr, name='get_qr_view'),
    path('tools/download_excel/<ou_slug>/', views.download_excel, name='download_excel'),
    path('tools/download_excel/<ou_slug>/<su_path>/', views.download_excel, name='download_excel'),

    # path('plotting/plot/', views.plot_view, name='plot_view'),
    path('plotting/plot/<ou_slug>/', views.plot_view, name='plot_view'),
    path('plotting/plot/<ou_slug>/<su_path>/', views.plot_view, name='plot_view'),

    path('crud/delete_shortened_url/<su_path>/', views.delete_shortened_url, name='delete_shortened_url'),
    path('crud/delete_outer_url/<ou_slug>/', views.delete_outer_url, name='delete_outer_url'),
]
