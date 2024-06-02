"""
URL configuration for audiocanvas project.

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
from django.urls import path, include, re_path
from home.views import (
    home_view

)
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from django.contrib.auth.decorators import login_required
from account.views import (
    registration_view,
    activate,
    logout_view,
    login_view,
    account_view,
    profile_view,
    delete_creation,
    heart_creation,
    sort_profile_view,
    resend_confirmation
)

from creation.views import (
    CreationWizardView, 
    save_rating,
    keyword_search,
    add_keywords,
    delete_keywords
    )

urlpatterns = [
    path('search/', keyword_search, name='search_keywords'),
    path('add_keyword/', add_keywords, name='add_keyword'),
    path('delete_keyword/', delete_keywords, name='delete_keyword'),
    path('logged_in/save-rating/', save_rating, name='save_rating'),
    path('admin/', admin.site.urls),
    path('logged_in/',login_required(CreationWizardView.as_view()), name="logged_in"),
    path('', home_view, name="home"),
    path('register/', registration_view, name="register"),
    path('logout/', logout_view, name="logout"),
    path('resend_confirmation/', resend_confirmation, name="resend_confirmation"),
    path('login/', login_view, name="login"),
    path('accountdetails/', account_view, name="accountdetails"),
    path('profile/', profile_view, name="profile"),
    path('profile/sort/', sort_profile_view, name='sort_profile'),
    path('delete-creation/', delete_creation, name="delete_creation"),
    path('heart-creation/', heart_creation, name="heart_creation"),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), 
        name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), 
        name='password_change'),

    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'),
     name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
     name='password_reset_complete'),

]

handler404 = 'home.views.custom_404_view' 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)