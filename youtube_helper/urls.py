"""youtube_helper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

from ythelperapp import views as main_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_views.main_page, name='main_page'),
    path('login/', main_views.login_page, name='login_page'),
    path('sign_up/', main_views.sign_up_page, name='sign_up_page'),
    path('download/', main_views.download_page, name='download_page'),
    path('download/video/', main_views.download_video, name="download_video"),
    path('download/audio/', main_views.download_audio, name="download_audio"),
]
