from django.urls import path
from song.views import *

app_name = 'song'
urlpatterns = [
    path('<uuid:id_konten>/', song, name='song'),
    path('add_song_playlist/<uuid:id_song>/', add_song_playlist, name='add_song_playlist'),
]
