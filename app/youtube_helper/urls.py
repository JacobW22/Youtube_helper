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
from django.contrib.auth import views as auth_views
from django.urls import path

from ythelperapp import views 

urlpatterns = [

    # Site

    path('admin/', admin.site.urls),
    path('', views.main_page, name='main_page'),
    
    path('manage_account/General', views.manage_account_General, name='manage_account_General'),
    path('manage_account/Overview', views.manage_account_Overview, name='manage_account_Overview'),
    path('manage_account/Private', views.manage_account_Private, name='manage_account_Private'),
    
    path('comments/', views.comments, name='comments'),
    
    path('ai_generator/', views.ai_page, name='ai_page'),
    path('ai_generator/<path:parameter>/<str:parameter_title>', views.ai_page, name='ai_page'),
    
    path('login/', views.login_page, name='login_page'),
    path('sign_up/', views.sign_up_page, name='sign_up_page'),
    path('log_out/', views.logoutUser, name='logout'),

    path('login/reset_password/', auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name='password_reset'),
    path('login/reset_password/sent', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"), name='password_reset_done'),
    path('login/reset_password/complete', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"), name='password_reset_complete'),

    path('login/reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),
    
    path('download/<path:parameter>', views.download_page, name='download_page'),
    path('download/<path:parameter><str:parameter_name>', views.download_page, name='download_page'),

    path('youtube_to_spotify/', views.youtube_to_spotify, name="youtube_to_spotify"),
    path('youtube_to_spotify/done/<path:account_url>', views.youtube_to_spotify_done, name="youtube_to_spotify_done"),


    # Api

    path('api/download_history/', views.RetrieveDownloadHistory.as_view({'get': 'list'})),
    path('api/prompts_history/', views.RetrievePromptsHistory.as_view({'get': 'list'})),
    path('api/filtered_comments_history/', views.RetrieveFilteredCommentsHistory.as_view({'get': 'list'})),
    path('api/transferred_playlists_history/', views.RetrieveTransferredPlaylistsHistory.as_view({'get': 'list'})),
]
