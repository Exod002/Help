# dashboard/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard and report pages
    #path('', views.dashboard_view, name='dashboard'),
    path('process_screenshot/', views.process_screenshot, name='process_screenshot'),
    path('report/', views.report_view, name='report'),
    path('download_pdf/', views.download_pdf, name='download_pdf'),

    # Authentication: registration, email verification, login, logout, and password reset
    path('register/', views.register, name='register'),
    path('verify_email/', views.verify_email, name='verify_email'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
