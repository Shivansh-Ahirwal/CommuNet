from django.urls import path, include
from chat import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('chat/<str:chat_id>/', views.chat_room_view, name='chat_room'),
    path('users/all/', views.fetch_users_modal, name='fetch_users_modal'),
    path('api/create-group/', views.create_group, name='create_group'),
]