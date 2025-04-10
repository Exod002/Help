# dashboard/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard and report pages
    path('dashboard/', views.dashboard, name='dashboard'),
    path('welcome/', views.welcome_page, name='welcome'),
    path('powerbi/', views.powerbi_report, name='powerbi_report'),
    path('screenshot/', views.take_screenshot, name='take_screenshot'),
    path('generate-report/', views.generate_report, name='generate_report'),
    path('download-report/', views.download_report, name='download_report'),

    # Authentication: registration, email verification, login, logout, and password reset
    path('register/', views.register, name='register'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
