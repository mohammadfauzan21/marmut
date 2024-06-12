from django.urls import path
from dashboardreguser.views import *

app_name = 'dashboardreguser'
urlpatterns = [
    path('kelolaplaylist/<uuid:id_playlist>/', kelolaplaylist, name='kelolaplaylist'),
    path('playsong/<uuid:id_konten>/', playsong, name='playsong'),
    path('userplaylist/', userplaylist, name='userplaylist'),
    path('delete_playlist/<uuid:id_user_playlist>/', delete_playlist, name='delete_playlist'),
    path('putar_lagu/<uuid:id_konten>/', putar_lagu, name='putar_lagu'),
    path('add_playlist/', add_playlist, name='add_playlist'),
    path('ubah_playlist/<uuid:id_playlist>/', ubah_playlist, name='ubah_playlist'),
    path('add_song_to_playlist/<uuid:id_playlist>/', add_song_to_playlist, name='add_song_to_playlist'),
    path('add_song_playlist/<uuid:id_song>/', add_song_playlist, name='add_song_playlist'),
    path('create_album/', create_album, name='create_album'),
    path('delete_album/<uuid:id_album>/', delete_album, name='delete_album'),
    path('create_song/<uuid:id_album>/', create_song, name='create_song'),
    path('kelolaalbum/<uuid:id_album>/', kelolaalbum, name='kelolaalbum'),
]