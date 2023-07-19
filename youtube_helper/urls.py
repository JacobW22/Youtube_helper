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
    path('manage_account/General', main_views.manage_account_General, name='manage_account_General'),
    path('manage_account/Overview', main_views.manage_account_Overview, name='manage_account_Overview'),
    path('manage_account/Private', main_views.manage_account_Private, name='manage_account_Private'),
    path('comments/', main_views.comments, name='comments'),
    path('ai_generator/', main_views.ai_page, name='ai_page'),
    path('ai_generator/<path:parameter>/<str:parameter_title>', main_views.ai_page, name='ai_page'),
    path('login/', main_views.login_page, name='login_page'),
    path('sign_up/', main_views.sign_up_page, name='sign_up_page'),
    path('log_out/', main_views.logoutUser, name='logout'),
    path('download/<path:parameter>', main_views.download_page, name='download_page'),
    path('download/<path:parameter><str:parameter_name>', main_views.download_page, name='download_page'),

]
