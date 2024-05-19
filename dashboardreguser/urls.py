from django.urls import path
from dashboardreguser.views import *

app_name = 'dashboardreguser'
urlpatterns = [
    path('', dashboarduser, name='dashboarduser'),
    path('kelolaplaylist/<uuid:id_playlist>/', kelolaplaylist, name='kelolaplaylist'),
    path('playsong/<uuid:id_konten>/', playsong, name='playsong'),
    path('userplaylist/', userplaylist, name='userplaylist'),
    path('chart/', chart, name='chart'),
    path('delete_playlist/<uuid:id_user_playlist>/', delete_playlist, name='delete_playlist'),
    path('add_playlist/', add_playlist, name='add_playlist'),
    path('ubah_playlist/<uuid:id_playlist>/', ubah_playlist, name='ubah_playlist'),
    path('add_song_to_playlist/<uuid:id_playlist>/', add_song_to_playlist, name='add_song_to_playlist'),
    path('add_song_playlist/<uuid:id_song>/', add_song_playlist, name='add_song_playlist')
]