from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('session/add/', views.add_workout_session, name='add_workout_session'),
    path('session/<int:session_id>/', views.workout_session_detail, name='workout_session_detail'),
    path('progress/', views.progress_chart, name='progress_chart'),
    path('exercise/add/', views.add_custom_exercise, name='add_custom_exercise'),
]
