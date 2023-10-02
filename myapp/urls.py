from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('upload/', views.upload, name='upload'),
    path('spotify_login/', views.spotify_login, name='spotify_login'),
    path('spotify_callback/', views.spotify_callback, name='spotify_callback'),
    path('files/<int:file_idx>/', views.files, name='files'),
    path('add_track/<int:file_idx>/', views.add_track, name='add_track'),
    path('user/', views.user, name='user'),
    path('user_logout/', views.user_logout, name='user_logout'),
]