"""MEDIA URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, re_path
from django.views.generic import TemplateView

from users import views

urlpatterns = [
    re_path(r'^profile/(?P<id>\d+)', views.user_page),
    re_path(r'^profile/$', views.user_page),
    re_path(r'^articles/$', views.tag_page),
    re_path(r'^logout/$', views.logout_page),
    path('', views.index),
    path('about/', TemplateView.as_view(template_name="about.html")),
    path('admin/', admin.site.urls),
]
