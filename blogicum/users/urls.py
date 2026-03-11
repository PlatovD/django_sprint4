from django.contrib.auth import views
from django.urls import path

import users.views as custom_views

urlpatterns = [
    path('auth/registration/', custom_views.UserCreateView.as_view(), name='registration'),
    path('auth/login/', custom_views.CustomLoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),

    path('auth/password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('auth/password_change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('auth/password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('auth/password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('auth/reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profile/<str:username>/', custom_views.UserProfileView.as_view(), name='profile'),
    path('profile/edit', custom_views.UserProfileUpdateView.as_view(), name='edit_profile')
]
