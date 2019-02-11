from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'spiritdashboard'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='spiritdashboard/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('claim/<str:key>/', views.claim_key, name='claim_key'),
    path('user_leaderboard/', views.UserLeaderboard.as_view(), name='user_leaderboard'),
    path('grade_leaderboard/', views.GradeLeaderboard.as_view(), name='grade_leaderboard'),
    path('completed/', views.completed, name='completed'),
    path('privacy/', views.privacy_policy, name='privacy_policy')
]
