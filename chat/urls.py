from django.urls import path
from chat import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Chat & Home
    path('', views.home, name='home'),
    path('chat/<str:chat_id>/', views.chat_room_view, name='chat_room'),

    # Users & Groups
    path('users/all/', views.fetch_users_modal, name='fetch_users_modal'),
    path('chat/create-group/', views.create_group, name='create_group'),

    # File Handling
    path('chat/upload/', views.upload_file, name='upload_file'),
    path('files/<str:file_id>/', views.serve_file, name='serve_file')
]
