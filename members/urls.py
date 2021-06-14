from django.contrib import admin
from django.urls import path, include
from .views import UserRegisterView, PasswordsChangeView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views 
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('user_update_details/', views.user_update_details, name='userUpdateDetails'),
    path('password/', PasswordsChangeView.as_view(template_name = 'registration/change-password.html'), name= 'password'),
    
    path('reset_password/',  views.password_reset_request, name="reset_password"),
    path('reset_password_sent', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_done.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)